import mysql.connector
import os

print('\n[INFO] Resetting data...\n')

# Creation of the tables, after having created the database
mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='styleup'
)
mycursor = mydb.cursor()


# Person table
query_delete = 'DELETE FROM Person;'
try:
    mycursor.execute(query_delete)
    mydb.commit()
    print('[INFO] Table \'Person\' successfully reset.')
except Exception as err:
    print('[ERROR] Something went wrong during the reset of the table \'Person\': '+str(err))


# Shirt table
query_delete = 'DELETE FROM Shirt;'
try:
    mycursor.execute(query_delete)
    mydb.commit()
    print('[INFO] Table \'Shirt\' successfully reset.')
except Exception as err:
    print('[ERROR] Something went wrong during the reset of the table \'Shirt\': '+str(err))


# Notification table
query_delete = 'DELETE FROM Notification;'
try:
    mycursor.execute(query_delete)
    mydb.commit()
    print('[INFO] Table \'Notification\' successfully reset.')
except Exception as err:
    print('[ERROR] Something went wrong during the reset of the table \'Notification\': '+str(err))


# Friend_of table
query_delete = 'DELETE FROM Friend_of;'
try:
    mycursor.execute(query_delete)
    mydb.commit()
    print('[INFO] Table \'Friend_of\' successfully reset.')
except Exception as err:
    print('[ERROR] Something went wrong during the reset of the table \'Friend_of\': '+str(err))


# Post table
query_delete = 'DELETE FROM Post;'
try:
    mycursor.execute(query_delete)
    mydb.commit()
    print('[INFO] Table \'Post\' successfully reset.')
except Exception as err:
    print('[ERROR] Something went wrong during the reset of the table \'Post\': '+str(err))


# Likes table
query_delete = 'DELETE FROM Likes;'
try:
    mycursor.execute(query_delete)
    mydb.commit()
    print('[INFO] Table \'Likes\' successfully reset.')
except Exception as err:
    print('[ERROR] Something went wrong during the reset of the table \'Likes\': '+str(err))


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
    query = 'INSERT INTO Shirt (shirt, shirt_name) VALUES (%s, %s);'
    values = (image, image_names[i])
    try:
        mycursor.execute(query, values)
        mydb.commit()
        print(f'[INFO] Shirt {image_names[i]} successfully uploaded!')
    except Exception as err:
        print(f'[ERROR] Something went wrong during the upload of the image {image_names[i]}: '+str(err))
    i+=1
i=0
    
print('\n[INFO] The system is ready!\n')