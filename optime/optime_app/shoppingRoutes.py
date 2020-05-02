from .app import *

############### SHOPPING ###############
@app.route('/shopping', methods=['GET', 'POST'])
@login_required
def shopping(task_storename=None, task_storeaddr=None, task_lat=None, task_lon=None, task_userProds=None):
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
    task_product = {}

    if request.method == 'POST':
        args = request.form
        categories = args.getlist('category')
        product = args['product']

        for i in range(len(categories)):
            if (categories[i] == "Grocery Store"):
                categories[i] = "Grocery"
    elif 'task_storename' in request.args:
        task_storename = request.args['task_storename']
        task_storeaddr = request.args['task_storeaddr']
        task_lat = request.args['task_lat']
        task_lon = request.args['task_lon']
        task_userProds = request.args.getlist('task_userProds')

        task_product = storeDB.stores.find_one(
            {'location': [{'lat' : task_lat}, {'lon' : task_lon}]})

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
    storeLocs=allStores, req=request.method,
    task_storename=task_storename,task_storeaddr=task_storeaddr,
    task_userProds=task_userProds,task_product=task_product,
    task_lat=task_lat,task_lon=task_lon, product=product, update=update), 200


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


@app.route('/shopping/refresh')
def refreshProdSelections():
    """
    Refresh the product stock fields if the user changes which store
    they would like to input data for
    """

    args = request.args

    storeName = args['name']
    storeLat = args['lat']
    storeLon = args['lon']
    task_userProds = []
    task_storeaddr = ""

    for t in g.user['shoppingTasks']:
        if (t['location'] == [storeLat, storeLon]):
            task_userProds = [item["productName"] for item in t["product"]]
            task_storeaddr = t['storeAddress']

    return redirect(url_for('.shopping',task_storename=storeName,task_storeaddr=task_storeaddr, task_userProds=task_userProds, task_lat=storeLat, task_lon=storeLon, update="true"))


@app.route('/shopping/delete_task')
def delete_shoppingTask():
    """
    Delete the user's shopping task from the database by index
    """

    args = request.args
    task_index = int(args['task_index'])
    db = get_db()
    task = g.user["shoppingTasks"][task_index]
    task_userProds = [item["productName"] for item in task["product"]]

    task_id = task["_id"]
    db.users.update_one({"_id": g.user["_id"]},
                        {"$pull": {"shoppingTasks": {"_id": task_id}}})
    if ('tasks' in args):
        return redirect(url_for('.shopping',task_storename=task['name'],task_storeaddr=task['storeAddress'], task_userProds=task_userProds, task_lat=task['location'][0], task_lon=task['location'][1], update="true"))
    return redirect(url_for('shopping'))


@app.route('/update')
def updateStore():
    """
    Update the stores database with crowdsourced store information
    """

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
        args.pop('category')

        newStocks = []
        for stock in args:
            if (args[stock] == ''):
                args[stock] = "No record"

            newStocks.append({'name':stock.split(':')[1], 'stock':productStorage[args[stock]], 'stockStr': args[stock]})

        storeDB = get_stores_db()
        storeDB.stores.update_one({"location": location}, {
                            "$set": {"hours": hours, "stock": newStocks}})
    return redirect(url_for('shopping'))
