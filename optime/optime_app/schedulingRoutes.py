from .app import *

############### SCHEDULING ###############
@app.route('/scheduling', methods=['GET', 'POST'])
@login_required
def scheduling():
    """
    Give the best time to go out based on a time window and duration
    """

    if request.method == 'POST':
        args = request.form

        # lat, lon, start_time, end_time, duration
        lat = g.user['lat']
        lon = g.user['lon']

        # finding timezone
        tz = tzwhere.tzwhere(forceTZ=True)
        local = tz.tzNameAt(float(lat), float(lon), forceTZ=True)

        # local start time
        start_time_local = datetime.strptime(args['start'],
                                             '%Y-%m-%d').replace(tzinfo=pytz.timezone(local))
        now_time_local = datetime.now(pytz.timezone(local))

        # if the user specified today as the starting date
        if start_time_local < now_time_local:
            start_time_utc = (datetime.utcnow().replace(tzinfo=pytz.utc) +
                              timedelta(seconds=10))
        else:
            start_time_utc = start_time_local.astimezone(pytz.utc)

        # local end time
        end_time_local = datetime.strptime(args['end'],
                                           '%Y-%m-%d').replace(tzinfo=pytz.timezone(local))
        end_time_utc = end_time_local.astimezone(pytz.utc)

        if (end_time_utc < start_time_utc):
            (start_time_utc, end_time_utc) = swap(start_time_utc, end_time_utc)
            (start_time_local, end_time_local) = swap(
                start_time_local, end_time_local)

        count = args['count']
        duration = int(args['duration'])
        name = args['name']

        if count == 'Minutes':
            duration *= 60
        elif count == 'Hours':
            duration *= 3600
        elif count == 'Days':
            duration *= 86400

        bestStartTime, bestEndTime = window_slider(lat, lon, start_time_utc,
                                                   end_time_utc, duration)
        bestStartTime = bestStartTime.astimezone(pytz.timezone(local))
        bestEndTime = bestEndTime.astimezone(pytz.timezone(local))

        task = {
            "_id": ObjectId(),
            "name": name,
            "start_time": bestStartTime,
            "end_time": bestEndTime,
        }

        db = get_db()
        db.users.update_one({"_id": g.user["_id"]}, {
            "$push": {"items": task}})

        return redirect(url_for('scheduling'))
    return render_template('scheduling.html', tasks=g.user['items']), 200


@app.route('/scheduling/delete_task')
def delete_task():
    """
    Delete the user's personal task from the database by index
    """

    args = request.args
    task_index = int(args['task_index'])
    db = get_db()
    task_id = g.user["items"][task_index]["_id"]
    db.users.update_one({"_id": g.user["_id"]},
                        {"$pull": {"items": {"_id": task_id}}})
    if ('tasks' in args):
        return redirect("/#personal-tasks")
    return redirect(url_for('scheduling'))
