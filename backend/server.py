import mysql.connector
import base64
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from utilities import get_timestamp, serialize_paints
from classes import PaintBackend

app = Flask(__name__)
CORS(app)

# Middleware per gestire le richieste preflight OPTIONS
@app.before_request
def before_request():
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
            "Access-Control-Allow-Headers": "Origin, X-Requested-With, Content-Type, Accept",
            "Access-Control-Allow-Credentials": "true",
        }
        return ("", 200, headers)
    

# DB setup
mydb = mysql.connector.connect(
    host='localhost',
    user='root1',
    password='root1',
    database='framesnap'
)
curr = mydb.cursor()


@app.route('/')
def fetch():
    return jsonify({"message":"The server is working", "status":200})


############################ ACCOUNT MANAGEMENT APIs #####################################
@app.route('/register', methods=['POST'])
def create_account():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    
    # The check about whether the username is correct or not is entirely done by the DBMS
    query = 'INSERT INTO Person (username, email, password) VALUES (%s, %s, %s);'
    values = (username, email, password,)
    try:
        curr.execute(query, values)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while inserting the new person: '+str(err))
        return jsonify({'message':'ERROR: The username is not valid.', 'status':400})
    
    return jsonify({"message":"You have registered successfully!", "status":200})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    query = 'SELECT username, email, password FROM Person WHERE email = %s;'
    values = (email,)
    curr.execute(query, values)
    result = curr.fetchall()
    
    for elem in result:
        if elem[2] == password:
            return jsonify({'message':'Login successfully!', 'username':elem[0], 'status':200})
        elif elem[2] != password:
            return jsonify({'message':'ERROR: Wrong username and/or password.', 'username':None, 'status':400})
    
    # If we get here, the email is wrong
    return jsonify({'message':'ERROR: Wrong email and/or password.', 'status':400})


@app.route('/updateAccount', methods=['POST'])
def update_account():
    data = request.get_json()
    old_username = data['old_username']
    username = data['username']
    email = data['email']
    password = data['password']
    profile_image = None
    try:
        profile_image = data['profile_image']
        profile_image = bytearray([(value + 256) % 256 for value in profile_image])
    except Exception as err:
        profile_image = None
        print(f"[ERROR] {str(err)}")
    
    if old_username is not None:
        if email != "":
            query = 'UPDATE Person SET email = %s WHERE username = %s;'
            values = (email, old_username)
            try:
                curr.execute(query, values)
                mydb.commit()
            except Exception as err:
                print('[ERROR] There was an error while modifying the account: '+str(err))
                return jsonify({'message':'ERROR: Account modification failed.', 'status':500})
            
        if password != "":
            query = 'UPDATE Person SET password = %s WHERE username = %s;'
            values = (password, old_username)
            try:
                curr.execute(query, values)
                mydb.commit()
            except Exception as err:
                print('[ERROR] There was an error while modifying the account: '+str(err))
                return jsonify({'message':'ERROR: Account modification failed.', 'status':500})
            
        if profile_image is not None:
            query = 'UPDATE Person SET profile_image = %s WHERE username = %s;'
            values = (profile_image, old_username)
            try:
                curr.execute(query, values)
                mydb.commit()
            except Exception as err:
                print('[ERROR] There was an error while modifying the account: '+str(err))
                return jsonify({'message':'ERROR: Account modification failed.', 'status':500})
            
        if username != "":
            query = 'UPDATE Person SET username = %s WHERE username = %s;'
            values = (username, old_username)
            try:
                curr.execute(query, values)
                mydb.commit()
            except Exception as err:
                print('[ERROR] There was an error while modifying the account: '+str(err))
                return jsonify({'message':'ERROR: Account modification failed.', 'status':500})
        
        return jsonify({"message":"Account modification successful!", "status":200})
    
    return jsonify({'message':'ERROR: Account modification failed.', 'status':500})


@app.route('/deleteAccount', methods=['POST'])
def delete_account():
    data = request.get_json()
    username = data['username']
    
    query = 'DELETE FROM Person WHERE username = %s;'
    values = (username,)
    try:
        curr.execute(query, values)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while deleting the account: '+str(err))
        return jsonify({'message':'ERROR: Delete operation was not successfully performed.', 'status':500})
    
    return jsonify({'message':'Your account has been successfully deleted!', 'status':200})


@app.route('/getProfileImage', methods=['GET'])
def get_profile_picture():
    username = request.args.get('username')
    
    query = 'SELECT profile_image FROM Person WHERE username = %s;'
    values = (username,)
    
    curr.execute(query, values)
    result = curr.fetchall()
    
    for elem in result:
        encoded_data = base64.b64encode(elem[0]).decode('utf-8')
        return jsonify({'profile_image':encoded_data, 'status':200})
    
    return jsonify({'profile_image':None, 'status':404})    


########################## PICTURES & POSTS MANAGEMENT APIs ##############################
@app.route('/getPaints', methods=['GET'])
def get_paint():
    paints = []

    query = 'SELECT id, paint, paint_name FROM Paint;'
    curr.execute(query)
    result = curr.fetchall()

    for elem in result:
        paint = {'id':elem[0], 'paint':base64.b64encode(elem[1]).decode('utf-8'), 'paintName':elem[2]}
        paints.append(paint)
    
    return jsonify({'paints':paints, 'status':200})


@app.route('/getPaintById', methods=['GET'])
def get_paint_by_id():
    paint_id = request.args.get('id')

    query = 'SELECT paint FROM Paint WHERE id = %s;'
    values = (paint_id,)

    curr.execute(query, values)
    result = curr.fetchall()

    for elem in result:
        encoded_data = base64.b64encode(elem[0]).decode('utf-8')
        return jsonify({'paint':encoded_data, 'status':200})
    
    return jsonify({'paint':None, 'status':404})


@app.route('/createPost', methods=['POST'])
def create_post():
    data = request.get_json()
    username = data['username']
    image_data = None
    try:
        image_data = data['imageData']
        image_data = base64.b64decode(image_data)
        image_data = bytearray([(value + 256) % 256 for value in image_data])
    except Exception as err:
        image_data = None
        print(f"[ERROR] {str(err)}")
        return jsonify({'message':'ERROR: Create post operation was not successfully performed.', 'status':500})
    
    timestamp = datetime.now()
    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    query = 'INSERT INTO Post (username, image_data, timestamp) VALUES (%s, %s, %s);'
    values = (username, image_data, timestamp)
    
    try:
        curr.execute(query, values)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while creating the post: '+str(err))
        return jsonify({'message':'ERROR: Create post operation was not successfully performed.', 'status':500})
    
    return jsonify({"message":"The post was successfully created!", "status":200})


@app.route('/deletePost', methods=['POST'])
def delete_post():
    data = request.get_json()
    post_id = data['id']
    
    query = 'DELETE FROM Post WHERE id = %s;'
    values = (post_id,)
    
    try:
        curr.execute(query, values)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while deleting the post: '+str(err))
        return jsonify({'message':'ERROR: Delete post operation was not successfully performed.', 'status':500})
    
    return jsonify({"message":"The post was successfully deleted!", "status":200})


############################## FRIENDS MANAGEMENT APIs ################################
@app.route('/getUsers', methods=['GET'])
def get_users():
    username = request.args.get('username')
    
    usernames = []
    
    query = "SELECT username FROM Person;"
    curr.execute(query)
    result = curr.fetchall()
    
    for user in result:
        if user[0] != username:
            usernames.append(str(user[0]))
    
    if len(usernames) == 0:
        return jsonify({"usernames":[], "status":404})
    
    return jsonify({"usernames":usernames, "status":200})


@app.route('/getUsersByUsername', methods=['GET'])
def get_users_by_username():
    usernames = []
    
    my_username = request.args.get('myUsername')
    username_search = request.args.get('usernameSearch')
    
    if username_search == "":
        return jsonify({'usernames':[], "status": 400})
    
    query = f"SELECT username from Person WHERE username REGEXP '{username_search}.*';"
    curr.execute(query)
    result = curr.fetchall()
    
    for user in result:
        if user[0] != my_username:
            usernames.append(str(user[0]))
            
    if len(usernames) == 0:
        return jsonify({'usernames':[], 'status':404})
    
    return jsonify({'usernames':usernames, 'status':200})


@app.route('/getUserByUsername', methods=['GET'])
def get_user_by_username():
    username = request.args.get('username')
    
    query = f"SELECT username, profile_image from Person WHERE username REGEXP '{username}.*';"
    curr.execute(query)
    result = curr.fetchall()
    
    for user in result:
        if user[1] is not None:
            return_user = {'username':str(user[0]), 'profileImage':base64.b64encode(user[1]).decode('utf-8')}
        else:
            return_user = {'username':str(user[0]), 'profileImage':""}
            
        return jsonify({'user':return_user, 'status':200})
    
    return jsonify({'user':[], 'status':404})


@app.route('/getNotifications', methods=['GET'])
def get_notifications():
    username = request.args.get('username')
    notifications = []
    
    query = 'SELECT notification_id, type, text FROM Notification WHERE username_to = %s AND notification_read = 0;'
    values = (username,)
    
    curr.execute(query, values)
    result = curr.fetchall()
    
    for elem in result:
        notifications.append({'id':elem[0], 'type':elem[1], 'text':elem[2]})
    
    return jsonify({'notifications':notifications, "status":200})


@app.route('/readNotification', methods=['POST'])
def read_notification():
    data = request.get_json()
    id = data['id']

    query = "UPDATE Notification SET notification_read = %s WHERE notification_id = %s;"
    values = (1, id)

    try:
        curr.execute(query, values)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while reading the notification: '+str(err))
        return jsonify({'message':'ERROR: Read notification operation was not successfully performed.', 'status':500})
    
    return jsonify({'message':'The notification has been read successfully!', 'status':200})


@app.route('/sendFriendshipRequest', methods=['POST'])
def send_friendship_request():
    data = request.get_json()
    username_from = data['usernameFrom']
    username_to = data['usernameTo']

    # Register Notification
    query_notification = 'INSERT INTO Notification (type, text, username_from, username_to) VALUES (%s, %s, %s, %s);'
    values_notification = ('friendship_request', f'{username_from} sent you a friend request', username_from, username_to,)

    try:
        curr.execute(query_notification, values_notification)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while sending the friendship request: '+str(err))
        return jsonify({'message':'ERROR: Send friendship request operation was not successfully performed.', 'status':500})
    

    # Register pending state in friend_of
    query_friend_of = 'INSERT INTO Friend_of (person1, person2, pending) VALUES (%s, %s, %s);'
    values_friend_of = (username_from, username_to, 1)
    
    try:
        curr.execute(query_friend_of, values_friend_of)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while sending the friendship request: '+str(err))
        return jsonify({'message':'ERROR: Send friendship request operation was not successfully performed.', 'status':500})


    return jsonify({"message":"Friendship request sent successfully!", "status":200})


@app.route('/acceptFriendshipRequest', methods=['POST'])
def accept_friendship_request():
    data = request.get_json()
    notification_id = data['notificationId']
    username_from = ""
    username_to = ""


    # Retrieve usernames from notification
    query_notification = 'SELECT username_from, username_to FROM Notification WHERE notification_id = %s;'
    values_notification = (notification_id,)

    curr.execute(query_notification, values_notification)
    result = curr.fetchone()
    username_from = result[0]
    username_to = result[1]

    print(f"[INFO] username_from = {username_from}; username_to = {username_to}")
    

    # Update pending status in Friend_of
    query_friend_of = 'UPDATE Friend_of SET pending = %s WHERE (person1 = %s AND person2 = %s) OR (person1 = %s AND person2 = %s);'
    values_friend_of = (0, username_from, username_to, username_to, username_from,)
    try:
        curr.execute(query_friend_of, values_friend_of)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while accepting the friendship request: '+str(err))
        return jsonify({'message':'ERROR: Accept friendship request operation was not successfully performed.', 'status':500})

    return jsonify({"message":f"{username_from} and {username_to} are now friends!", "status":200})


@app.route('/refuseFriendshipRequest', methods=['POST'])
def refuse_friendship_request():
    data = request.get_json()
    notification_id = data['notificationId']
    username_from = None
    username_to = None


    # Retrieve usernames from notification
    query_notification = 'SELECT username_from, username_to FROM Notification WHERE notification_id = %s;'
    values_notification = (notification_id,)

    curr.execute(query_notification, values_notification)
    result = curr.fetchone()
    if result is not None:
        username_from = result[0]
        username_to = result[1]
    

    # Delete corresponding row in Friend_of
    query_friend_of = 'DELETE FROM Friend_of WHERE (person1 = %s AND person2 = %s) OR (person1 = %s AND person2 = %s);'
    values_friend_of = (username_from, username_to, username_to, username_from,)
    try:
        curr.execute(query_friend_of, values_friend_of)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while refusing the friendship request: '+str(err))
        return jsonify({'message':'ERROR: Refuse friendship request operation was not successfully performed.', 'status':500})

    return jsonify({"message":"Friendship request has been successfully refused.", "status":200})


@app.route('/removeFriend', methods=['POST'])
def remove_friend():
    data = request.get_json()
    username_from = data['usernameFrom']
    username_to = data['usernameTo']

    # Remove friendship
    query_friend_of = 'DELETE FROM Friend_of WHERE (person1 = %s AND person2 = %s) OR (person1 = %s AND person2 = %s);'
    values_friend_of = (username_from, username_to, username_to, username_from,)
    try:
        curr.execute(query_friend_of, values_friend_of)
        mydb.commit()
    except Exception as err:
        print('[ERROR] There was an error while removing the friendship: '+str(err))
        return jsonify({'message':'ERROR: Remove friendship operation was not successfully performed.', 'status':500})

    return jsonify({"message":f"{username_from} and {username_to} are no longer friends.", "status":200})


@app.route('/getFriendsPosts', methods=['GET'])
def get_friends_posts():
    username = request.args.get('username')
    friends = []
    posts = []

    # Get friends (bilateral relation!)
    query_friend_of = 'SELECT person1 FROM Friend_of WHERE person2 = %s AND pending = %s;'
    values_friend_of = (username, False,)
    curr.execute(query_friend_of, values_friend_of)
    result = curr.fetchall()

    for elem in result:
        friends.append(elem[0])

    query_friend_of = 'SELECT person2 FROM Friend_of WHERE person1 = %s AND pending = %s;'
    values_friend_of = (username, False,)
    curr.execute(query_friend_of, values_friend_of)
    result = curr.fetchall()

    for elem in result:
        friends.append(elem[0])

    if len(friends) == 0:
        return jsonify({"message":"No friends found for that username.", "status":404})


    # For each friend, get posts
    for friend_username in friends:
        query = 'SELECT id, image_data, timestamp FROM Post WHERE username = %s;'
        values = (friend_username,)

        curr.execute(query, values)
        result = curr.fetchall()

        for elem in result:
            posts.append(elem)
        
    if len(posts) == 0:
        return jsonify({"message":"No posts found.", "status":404})

    # Order the posts by temporal order
    sorted_posts = sorted(posts, key=get_timestamp)

    return jsonify({"posts":sorted_posts, "status":200})


@app.route('/getPostsByUsername', methods=['GET'])
def get_posts_by_username():
    username = request.args.get('username')
    loggedUser = request.args.get('loggedUser')
    liked = False
    posts = []

    # Get posts
    query = 'SELECT id, image_data, likes FROM Post WHERE username = %s;'
    values = (username,)

    curr.execute(query, values)
    result = curr.fetchall()
    # result = result.reverse()

    for elem in result:
        if elem[1] is None:
            print("ERROR")
        else:
            query2 = 'SELECT person FROM Likes WHERE post = %s;'
            values2 = (elem[0],)
            
            curr.execute(query2, values2)
            result = curr.fetchall()
            for element in result:
                if element[0] == loggedUser:
                    liked = True

            post = {'id':elem[0], 'imageData':base64.b64encode(bytearray(elem[1])).decode('utf-8'), 'username':username, 'likes':str(elem[2]), 'likedByLoggedUser':liked}
            posts.append(post)

    if len(posts) == 0:
        return jsonify({"posts":[], "status":404})

    return jsonify({"posts":posts, "status":200})


@app.route('/getFriends', methods=['GET'])
def get_friends():
    username = request.args.get('username')
    friends = set()
    friends_list = []

    query1 = 'SELECT person1 FROM Friend_of WHERE person2 = %s AND pending=%s;'
    query2 = 'SELECT person2 FROM Friend_of WHERE person1 = %s AND pending=%s;'
    values = (username, 0)

    curr.execute(query1, values)
    result = curr.fetchall()
    for elem in result:
        friends.add(elem[0])

    curr.execute(query2, values)
    result = curr.fetchall()
    for elem in result:
        friends.add(elem[0])

    for elem in friends:
        friends_list.append(elem)

    if len(friends_list) == 0:
        return jsonify({'friends':[], 'status':404})
    
    return jsonify({'friends':friends_list, 'status':200})


@app.route('/areFriends', methods=['POST'])
def are_friends():
    data = request.get_json()
    user1 = data['user1']
    user2 = data['user2']

    query = 'SELECT pending FROM Friend_of WHERE ((person1=%s AND person2=%s) OR (person2=%s AND person1=%s));'
    values = (user1, user2, user1, user2)

    curr.execute(query, values)
    result = curr.fetchall()

    for elem in result:
        if elem[0] == 0:
            return jsonify({'result':0, 'status':200})
        elif elem[0] == 1:
            return jsonify({'result':1, 'status':200})
    
    return jsonify({'result':2, 'status':200})



########################### INTERACTIONS MANAGEMENT APIs #################################
@app.route('/likePost', methods=['POST'])
def like_post():
    data = request.get_json()
    username = data['username']
    post_id = data['post']
    username_to = ""

    # Get "like receiver"
    query_get_post_owner = 'SELECT username FROM Post WHERE id = %s;'
    values_get_post_owner = (post_id,)
    curr.execute(query_get_post_owner, values_get_post_owner)
    result = curr.fetchall()
    for elem in result:
        username_to = elem[0]
    
    if username_to == "":
        return jsonify({'message':'ERROR: There is no post having the provided ID.', 'status':500})

    
    # Insert the person who liked the post
    query = 'INSERT INTO Likes (person, post) VALUES (%s, %s);'
    values = (username, post_id)
    
    try:
        curr.execute(query, values)
        mydb.commit()


        # Increase number of likes to that post
        query2 = 'UPDATE Post SET likes = likes + 1 WHERE id = %s;'
        values2 = (post_id,)

        try:
            curr.execute(query2, values2)
            mydb.commit()


            # Send notification to the like receiver (only if the like receiver is not myself! :P)
            if username != username_to:
                query3 = 'INSERT INTO Notification (type, text, username_from, username_to) VALUES (%s, %s, %s, %s);'
                values3 = ('like', f'{username} liked your post.', username, username_to)

                try:
                    curr.execute(query3, values3)
                    mydb.commit()
                except Exception as err:
                    print('[ERROR] There was an error while inserting the like: '+str(err))
                    return jsonify({'message':'ERROR: Like operation was not successfully performed.', 'status':500})


        except Exception as err:
            print('[ERROR] There was an error while inserting the like: '+str(err))
            return jsonify({'message':'ERROR: Like operation was not successfully performed.', 'status':500})


    except Exception as err:
        print('[ERROR] There was an error while inserting the like: '+str(err))
        return jsonify({'message':'ERROR: Like operation was not successfully performed.', 'status':500})
    
    return jsonify({"message":"You liked the post successfully!", "status":200})


@app.route('/unlikePost', methods=['POST'])
def unlike_post():
    data = request.get_json()
    username = data['username']
    post_id = data['post']

    query = 'DELETE FROM Likes WHERE person = %s AND post = %s;'
    values = (username, post_id)

    try:
        curr.execute(query, values)
        mydb.commit()

        query2 = 'UPDATE Post SET likes = likes - 1 WHERE id = %s;'
        values2 = (post_id,)

        try:
            curr.execute(query2, values2)
            mydb.commit()
        except Exception as err:
            print('[ERROR] There was an error while removing the like: '+str(err))
            return jsonify({'message':'ERROR: Unlike operation was not successfully performed.', 'status':500})


    except Exception as err:
        print('[ERROR] There was an error while removing the like: '+str(err))
        return jsonify({'message':'ERROR: Unlike operation was not successfully performed.', 'status':500})
    
    return jsonify({"message":"You unliked the post successfully!", "status":200})



##############################################################################################################
if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)