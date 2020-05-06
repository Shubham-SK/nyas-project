from .app import *

############### SHOPPING ###############
@app.route('/shopping', methods=['GET', 'POST'])
@login_required
def shopping():
    """
    Process user's search request for stores, manage redirects for deleting a task,
    selecting a store, and crowdsourcing
    """

    print('Getting request for stores')
    # lat, lon, max_locations, k, categories, product
    lat = g.user['lat']
    lon = g.user['lon']
    max_locations = 20
    k = 3
    categories = ['Grocery']
    product = None
    allStores = []
    storeDB = get_stores_db()

    if request.method == 'POST':
        args = request.form
        categories = args.getlist('category')
        product = args['product']

        for i in range(len(categories)):
            if (categories[i] == "Grocery Store"):
                categories[i] = "Grocery"

    if 'update' in request.args:
        update = 'true'
    else:
        update = 'false'

    # Sample store: ['Walmart', [37.72945007660575, -121.92957003664371], '9100 Alcosta Blvd, San Ramon, California, 94583']
    storesArr = get_safest_stores(lat, lon, max_locations, k, categories)

    for store in storesArr:
        storeLat = str(store[1][0])
        storeLon = str(store[1][1])
        allStores.append(constructStore(lat, lon, ObjectId(), store[0], storeLat, storeLon, store[2], product))

    allProducts = getAllProducts()

    return render_template('shopping.html', userLat=lat, userLon=lon,
    shoppingTasks=g.user['shoppingTasks'], allProducts=allProducts,
    storeLocs=allStores, req=request.method, update=update, product=product), 200


@app.route('/selectStore')
def selectStore():
    """
    Process the user's request to add a store to their shopping tasks
    - Register/update a store with the product specified
    - Update the user's shopping tasks with the product they want
    """

    params = []
    for i in request.args:
        params.append(request.args[i])

    allLocs = [list(task.values())[3] for task in g.user['shoppingTasks']]

    lat, lon, id, name, storeLat, storeLon, storeAddress, product = params
    store = constructStore(lat, lon, id, name, storeLat, storeLon, storeAddress, product)
    newProduct = store.pop("product")[0]

    db = get_db()
    storeDB = get_stores_db()

    if ([storeLat, storeLon] not in allLocs):
        db.users.update_one({"_id": g.user["_id"]},
        {"$push": {"shoppingTasks": constructStore(lat, lon, id, name, storeLat, storeLon, storeAddress, product)}})
    else:
        db.users.update_one(
            {"_id": g.user["_id"]},
            {"$addToSet" : { "shoppingTasks.$[elem].product" : newProduct }},
            upsert=True,
            array_filters=[ {"elem.location" : [storeLat,storeLon]}]
        )

    storeVal = storeDB.stores.find_one(
        {'location': [{'lat' : storeLat}, {'lon' : storeLon}]})
    if (storeVal == None):
        # The user's store is not in the database
        registerStore(ObjectId(), storeLat, storeLon, product)

    else:
        # The user's store is in the database, and the products array needs to be updated
        storeDB.stores.update_one(
            {'location': [{'lat' : storeLat}, {'lon' : storeLon}], 'stock.name': {'$ne': newProduct["productName"]}},
            {"$addToSet" : {"stock": {'name': newProduct["productName"], 'stock': -1, 'stockStr': "No record"}}}
        )

    return redirect(url_for('shopping'))

@app.route('/shopping/delete_task')
def delete_shoppingTask():
    """
    Delete the user's shopping task from the database by index
    """

    args = request.args
    task_index = int(args['task_index'])
    db = get_db()
    task = g.user["shoppingTasks"][task_index]

    task_id = task["_id"]
    db.users.update_one({"_id": g.user["_id"]},
                        {"$pull": {"shoppingTasks": {"_id": task_id}}})
    # if ('tasks' in args):
    #     return redirect(url_for('.shopping',task_storename=task['name'],task_storeaddr=task['storeAddress'], task_userProds=task_userProds, task_lat=task['location'][0], task_lon=task['location'][1], update="true"))

    if ('passVal' in args):
        return redirect(url_for('index'))

    return redirect(url_for('shopping'))


@app.route('/update')
def updateStore():
    """
    Update the stores database with crowdsourced store information
    """
    print("\n\nUPDATE RECIEVED")
    args = request.args.to_dict()
    # The minimum number of parameters is 1 (the store name)
    if (len(args) > 1):
        location = [{'lat' : args['lat']}, {'lon' : args['lon']}]
        # [:5] to always store 'HH:MM' instead of 'HH:MM:00'
        hours = {'open': args['open'][:5], 'close': args['close'][:5]}
        args.pop('lat')
        args.pop('lon')
        args.pop('open')
        args.pop('close')
        task_index = args.pop('task_index')

        newStocks = []
        for stock in args:
            if (args[stock] == ''):
                args[stock] = "No record"

            newStocks.append({'name':stock.split(':')[1], 'stock':productStorage[args[stock]], 'stockStr': args[stock]})

        storeDB = get_stores_db()
        storeDB.stores.update_one({"location": location}, {
                            "$set": {"hours": hours, "stock": newStocks}})

    return redirect(url_for('.delete_shoppingTask',task_index=task_index,passVal=True))
