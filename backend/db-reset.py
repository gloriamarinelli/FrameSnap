import mysql.connector
import os

print('\n[INFO] Resetting database...\n')

# Creation of the database
mydb = mysql.connector.connect(
    host='localhost',
    user='root1',
    password='root1'
)
cursor = mydb.cursor()
try:
    cursor.execute('DROP DATABASE IF EXISTS framesnap;')
    cursor.execute('CREATE DATABASE IF NOT EXISTS framesnap;')
    mydb.commit()
    print('[INFO] Database \'framesnap\' successfully created.')
except Exception as err:
    print('[ERROR] Something went wrong during the creation of the database \'framesnap\': '+str(err))
mydb.close()


# Creation of the tables, after having created the database
mydb = mysql.connector.connect(
    host='localhost',
    user='root1',
    password='root1',
    database='framesnap'
)
mycursor = mydb.cursor()


# Person table
person_drop = 'DROP TABLE IF EXISTS Person;'
person_table = '''
CREATE TABLE IF NOT EXISTS Person (
    username VARCHAR(100) PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    profile_image LONGBLOB,
    UNIQUE (email)
);
'''
try:
    mycursor.execute(person_drop)
    mycursor.execute(person_table)
    mydb.commit()
    print('[INFO] Table \'Person\' successfully created.')
except Exception as err:
    print('[ERROR] Something went wrong during the creation of the table \'Person\': '+str(err))


# Paint table
paint_drop = 'DROP TABLE IF EXISTS Paint;'
paint_table = '''
CREATE TABLE IF NOT EXISTS Paint (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paint LONGBLOB NOT NULL,
    paint_name VARCHAR(100),
    paint_year VARCHAR(4)
);
'''
try:
    mycursor.execute(paint_drop)
    mycursor.execute(paint_table)
    mydb.commit()
    print('[INFO] Table \'Paint\' successfully created.')
except Exception as err:
    print('[ERROR] Something went wrong during the creation of the table \'Paint\': '+str(err))


# Notification table
notification_drop = 'DROP TABLE IF EXISTS Notification;'
notification_table = '''
CREATE TABLE IF NOT EXISTS Notification (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    text VARCHAR(255) NOT NULL,
    username_from VARCHAR(100) NOT NULL,
    username_to VARCHAR(100) NOT NULL,
    notification_read TINYINT NOT NULL DEFAULT 0,
    FOREIGN KEY (username_from) 
        REFERENCES Person (username)
        ON DELETE CASCADE,
    FOREIGN KEY (username_to)
        REFERENCES Person (username)
        ON DELETE CASCADE,
    CONSTRAINT type_constraint 
        CHECK (type='like' OR type='friendship_request'),
    CONSTRAINT usernames_constraint
        CHECK (username_from <> username_to),
    CONSTRAINT read_constraint
        CHECK (notification_read=0 OR notification_read=1)
);
'''
try:
    mycursor.execute(notification_drop)
    mycursor.execute(notification_table)
    mydb.commit()
    print('[INFO] Table \'Notification\' successfully created.')
except Exception as err:
    print('[ERROR] Something went wrong during the creation of the table \'Notification\': '+str(err))


# Friend_of table
friend_of_drop = 'DROP TABLE IF EXISTS Friend_of;'
friend_of_table = '''
CREATE TABLE IF NOT EXISTS Friend_of (
    person1 VARCHAR(100) NOT NULL,
    person2 VARCHAR(100) NOT NULL,
    pending TINYINT NOT NULL DEFAULT 1,
    CONSTRAINT PK_Friend_of 
        PRIMARY KEY (person1, person2),
    FOREIGN KEY (person1) 
        REFERENCES Person (username)
        ON DELETE CASCADE,
    FOREIGN KEY (person2) 
        REFERENCES Person (username)
        ON DELETE CASCADE,
    CONSTRAINT person_constraint 
        CHECK (person1 <> person2)
);
'''
try:
    mycursor.execute(friend_of_drop)
    mycursor.execute(friend_of_table)
    mydb.commit()
    print('[INFO] Table \'Friend_of\' successfully created.')
except Exception as err:
    print('[ERROR] Something went wrong during the creation of the table \'Friend_of\': '+str(err))


# Post table
post_drop = 'DROP TABLE IF EXISTS Post;'
post_table = '''
CREATE TABLE IF NOT EXISTS Post (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    image_data LONGBLOB NOT NULL,
    timestamp DATETIME NOT NULL,
    likes INT NOT NULL DEFAULT 0,
    FOREIGN KEY (username) 
        REFERENCES Person (username)
        ON DELETE CASCADE
);
'''
try:
    mycursor.execute(post_drop)
    mycursor.execute(post_table)
    mydb.commit()
    print('[INFO] Table \'Post\' successfully created.')
except Exception as err:
    print('[ERROR] Something went wrong during the creation of the table \'Post\': '+str(err))


# Likes table
likes_drop = 'DROP TABLE IF EXISTS Likes;'
likes_table = '''
CREATE TABLE IF NOT EXISTS Likes (
    person VARCHAR(100) NOT NULL,
    post INT NOT NULL,
    CONSTRAINT PK_likes 
        PRIMARY KEY (person, post),
    FOREIGN KEY (person) 
        REFERENCES Person(username)
        ON DELETE CASCADE,
    FOREIGN KEY (post) 
        REFERENCES Post(id)
        ON DELETE CASCADE
);
'''
try:
    mycursor.execute(likes_drop)
    mycursor.execute(likes_table)
    mydb.commit()
    print('[INFO] Table \'Likes\' successfully created.')
except Exception as err:
    print('[ERROR] Something went wrong during the creation of the table \'Likes\': '+str(err))


# Load images into the database
print("\n")
image_paths = []
image_names = []
images = []
i = 0

for image_path in os.listdir("./images"):
    image_names.append(image_path[:-4])
    image_paths.append("./images/"+image_path)

for image in image_paths:
    with open(image, "rb") as image_file:
        images.append(image_file.read())

for image in images:
    query = 'INSERT INTO Paint (paint, paint_name, paint_year) VALUES (%s, %s, %s);'
    values = (image, image_names[i], "1800")
    try:
        mycursor.execute(query, values)
        mydb.commit()
        print(f'[INFO] Paint {image_names[i]} successfully uploaded!')
    except Exception as err:
        print(f'[ERROR] Something went wrong during the upload of the image {image_names[i]}: '+str(err))
    i+=1
i=0
    
print('\n[INFO] The system is ready!\n')