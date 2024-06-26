#!flask/bin/python
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'utils')))
from env import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_REGION, PHOTOGALLERY_S3_BUCKET_NAME, RDS_DB_HOSTNAME, RDS_DB_USERNAME, RDS_DB_PASSWORD, RDS_DB_NAME
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import render_template, redirect
import time
import exifread
import json
import uuid
import boto3
import pytz
import pymysql.cursors
from datetime import datetime
from pytz import timezone
from botocore.exceptions import ClientError

"""
    INSERT NEW LIBRARIES HERE (IF NEEDED)
"""





"""
"""

app = Flask(__name__, static_url_path="")

UPLOAD_FOLDER = os.path.join(app.root_path,'static','media')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getExifData(path_name):
    f = open(path_name, 'rb')
    tags = exifread.process_file(f)
    ExifData={}
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            key="%s"%(tag)
            val="%s"%(tags[tag])
            ExifData[key]=val
    return ExifData



def s3uploading(filename, filenameWithPath, uploadType="photos"):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                       
    bucket = PHOTOGALLERY_S3_BUCKET_NAME
    path_filename = uploadType + "/" + filename

    s3.upload_file(filenameWithPath, bucket, path_filename)  
    s3.put_object_acl(ACL='public-read', Bucket=bucket, Key=path_filename)
    return f'''http://{PHOTOGALLERY_S3_BUCKET_NAME}.s3.amazonaws.com/{path_filename}'''

def get_database_connection():
    conn = pymysql.connect(host=RDS_DB_HOSTNAME,
                             user=RDS_DB_USERNAME,
                             password=RDS_DB_PASSWORD,
                             db=RDS_DB_NAME,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    return conn

@app.route('/album/<string:albumID>/photo/<string:photoID>/deletePhoto', methods=['GET', 'POST'])
def deletePhoto(albumID, photoID):
    if request.method == 'POST':
        conn=get_database_connection()
        cursor = conn.cursor ()
        statement = f'''DELETE FROM photogallerydb.Photo WHERE albumID="{albumID}" and photoID="{photoID}";'''
            
        result = cursor.execute(statement)
        conn.commit()
        conn.close()
    return redirect(f'''/album/{albumID}''')

@app.route('/album/<string:albumID>/deleteAlbum', methods=['GET', 'POST'])
def deleteAlbum(albumID):
    if request.method == 'POST':
        conn=get_database_connection()
        cursor = conn.cursor ()
        statement = f'''DELETE FROM photogallerydb.Album WHERE albumID="{albumID}";'''
            
        result = cursor.execute(statement)
        conn.commit()
        conn.close()
    return redirect(f'''/''')



@app.route('/album/<string:albumID>/photo/<string:photoID>/updatePhoto', methods=['GET', 'POST'])
def updatePhoto(albumID, photoID):
    if request.method == 'POST':
        titles = request.form['title']
        descriptions = request.form['description']
        tagss = request.form['tags']
        conn=get_database_connection()
        cursor = conn.cursor ()
        statement = f'''UPDATE photogallerydb.Photo SET title= %s, description= %s, tags= %s WHERE albumID= %s and photoID= %s'''

        Title = titles
        Description = descriptions
        Tags = tagss
        AlbumIDs = albumID
        PhotoIDs = photoID
        
        
        input = (Title, Description, Tags, AlbumIDs, PhotoIDs)
            
        result = cursor.execute(statement, input)
        conn.commit()
        conn.close()
        return redirect(f'''/album/{albumID}/photo/{photoID}''')
    else:
        return render_template('updatephoto.html')

@app.route('/album/<string:albumID>/photo/<string:photoID>/tempUpdatePhoto')
def tempUpdatePhoto(albumID, photoID):
    return render_template('updatephoto.html', albumID=albumID, photoID=photoID)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':    
        username = request.form['username']
        password = request.form['password']
        response = table2.scan(FilterExpression=Attr('username').eq(username) & Attr('password').eq(password))
        results = response['Items']

        if len(results) > 0:
            return redirect(f'''/''')
        else:
            return render_template('login.html')

@app.route('/logout')
def logout():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        emailID = request.form['email']
        password = request.form['password']
        userID = uuid.uuid4()

        createdAtlocalTime = datetime.now().astimezone()
        updatedAtlocalTime = datetime.now().astimezone()

        createdAtUTCTime = createdAtlocalTime.astimezone(pytz.utc)
        updatedAtUTCTime = updatedAtlocalTime.astimezone(pytz.utc)
    if request.method == 'POST':

        conn=get_database_connection()
        cursor = conn.cursor ()
        statement = f'''INSERT INTO photogallerydb.User (userID, emailID, username, name, password, createdAtUTCTime, updatedAtUTCTime) VALUES ("{userID}", "{emailID}", "{username}", "{name}", "{password}", "{createdAtUTCTime}", "{updatedAtUTCTime}");'''
            
        result = cursor.execute(statement)
        conn.commit()
        conn.close()

        return redirect(f'''/signup/confirmemail''')

    else:

        return render_template('signup.html')


@app.route('/signup/tempconfirmemail', methods=['GET', 'POST'])
def tempconfirmemail():
    return render_template('confirmemail.html')

@app.route('/signup/confirmation1email/<string:token>')
def confirm1(token):
    return redirect('/login')

@app.route('/signup/confirmemail', methods=['GET', 'POST'])
def confirmemail():
        email = "mhussain43@gatech.edu"
        serializer = URLSafeTimedSerializer("iuhGQnw6ZyJvN1A2OyNPLOdV+94OEOVI9oOoBCSR")
        token = serializer.dumps(email, salt="iuhGQnw6ZyJvN1A2OyNPLOdV+94OEOVI9oOoBCSR")
        print(token)
        # eyJpZCI6NSwibmFtZSI6Iml0c2Rhbmdlcm91cyJ9.6YP6T0BaO67XP--9UzTrmurXSmg
        try:
            email = serializer.loads(
                token,
                salt='iuhGQnw6ZyJvN1A2OyNPLOdV+94OEOVI9oOoBCSR',
                max_age=600
            )
            print(token)
            #mhussain43@gatech.edu
        except Exception as e:
            print("expired token")
            return render_template('signup.html')
        
        # Create a new SES resource and specify a region.
        ses = boto3.client('ses',
                         region_name=AWS_REGION,
                         aws_access_key_id=AWS_ACCESS_KEY,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        SENDER = 'rahilhussain10@gmail.com'
        RECEIVER = 'mhussain43@gatech.edu'
        # Try to send the email.
        try:
            #Provide the contents of the email.
            response = ses.send_email(
                Destination={
                    'ToAddresses': [RECEIVER],
                },
                Message={
                    'Body': {
                        'Text': {
                           'Data': f'http://ec2-35-171-3-254.compute-1.amazonaws.com:5000/logout'
                        },
                    },
                    'Subject': {
                       'Data': 'Email Confirmation'
                    },
                },
                Source=SENDER
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
        
        return redirect('/signup')

@app.route('/signup/tempcancelaccount', methods=['GET', 'POST'])
def tempcancelaccount():
    return render_template('cancelaccount.html')

@app.route('/signup/cancelaccount', methods=['GET', 'POST'])
def cancelaccount(emailID):
    if request.method == 'POST':

        conn=get_database_connection()
        cursor = conn.cursor ()
        statement = f'''DELETE FROM photogallerydb.User WHERE emailID="{emailID}";'''
            
        result = cursor.execute(statement)
        conn.commit()
        conn.close()

        return redirect(f'''/logout''')
"""
"""

"""
    INSERT YOUR NEW ROUTE HERE (IF NEEDED)
"""





"""
"""

@app.errorhandler(400)
def bad_request(error):
    """ 400 page route.

    get:
        description: Endpoint to return a bad request 400 page.
        responses: Returns 400 object.
    """
    return make_response(jsonify({'error': 'Bad request'}), 400)



@app.errorhandler(404)
def not_found(error):
    """ 404 page route.

    get:
        description: Endpoint to return a not found 404 page.
        responses: Returns 404 object.
    """
    return make_response(jsonify({'error': 'Not found'}), 404)



@app.route('/', methods=['GET'])
def home_page():
    """ Home page route.

    get:
        description: Endpoint to return home page.
        responses: Returns all the albums.
    """
    conn=get_database_connection()
    cursor = conn.cursor ()
    cursor.execute("SELECT * FROM photogallerydb.Album;")
    results = cursor.fetchall()
    conn.close()
    
    items=[]
    for item in results:
        album={}
        album['albumID'] = item['albumID']
        album['name'] = item['name']
        album['description'] = item['description']
        album['thumbnailURL'] = item['thumbnailURL']

        createdAt = datetime.strptime(str(item['createdAt']), "%Y-%m-%d %H:%M:%S")
        createdAt_UTC = timezone("UTC").localize(createdAt)
        album['createdAt']=createdAt_UTC.astimezone(timezone("US/Eastern")).strftime("%B %d, %Y")

        items.append(album)

    return render_template('index.html', albums=items)



@app.route('/createAlbum', methods=['GET', 'POST'])
def add_album():
    """ Create new album route.

    get:
        description: Endpoint to return form to create a new album.
        responses: Returns all the fields needed to store new album.

    post:
        description: Endpoint to send new album.
        responses: Returns user to home page.
    """
    if request.method == 'POST':
        uploadedFileURL=''
        file = request.files['imagefile']
        name = request.form['name']
        description = request.form['description']

        if file and allowed_file(file.filename):
            albumID = uuid.uuid4()
            
            filename = file.filename
            filenameWithPath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filenameWithPath)
            
            uploadedFileURL = s3uploading(str(albumID), filenameWithPath, "thumbnails");

            conn=get_database_connection()
            cursor = conn.cursor ()
            statement = f'''INSERT INTO photogallerydb.Album (albumID, name, description, thumbnailURL) VALUES ("{albumID}", "{name}", "{description}", "{uploadedFileURL}");'''
            
            result = cursor.execute(statement)
            conn.commit()
            conn.close()

        return redirect('/')
    else:
        return render_template('albumForm.html')



@app.route('/album/<string:albumID>', methods=['GET'])
def view_photos(albumID):
    """ Album page route.

    get:
        description: Endpoint to return an album.
        responses: Returns all the photos of a particular album.
    """
    conn=get_database_connection()
    cursor = conn.cursor ()
    # Get title
    statement = f'''SELECT * FROM photogallerydb.Album WHERE albumID="{albumID}";'''
    cursor.execute(statement)
    albumMeta = cursor.fetchall()
    
    # Photos
    statement = f'''SELECT photoID, albumID, title, description, photoURL FROM photogallerydb.Photo WHERE albumID="{albumID}";'''
    cursor.execute(statement)
    results = cursor.fetchall()
    conn.close() 
    
    items=[]
    for item in results:
        photos={}
        photos['photoID'] = item['photoID']
        photos['albumID'] = item['albumID']
        photos['title'] = item['title']
        photos['description'] = item['description']
        photos['photoURL'] = item['photoURL']
        items.append(photos)

    return render_template('viewphotos.html', photos=items, albumID=albumID, albumName=albumMeta[0]['name'])



@app.route('/album/<string:albumID>/addPhoto', methods=['GET', 'POST'])
def add_photo(albumID):
    """ Create new photo under album route.

    get:
        description: Endpoint to return form to create a new photo.
        responses: Returns all the fields needed to store a new photo.

    post:
        description: Endpoint to send new photo.
        responses: Returns user to album page.
    """
    if request.method == 'POST':    
        uploadedFileURL=''
        file = request.files['imagefile']
        title = request.form['title']
        description = request.form['description']
        tags = request.form['tags']

        if file and allowed_file(file.filename):
            photoID = uuid.uuid4()
            filename = file.filename
            filenameWithPath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filenameWithPath)            
            
            uploadedFileURL = s3uploading(filename, filenameWithPath);
            
            ExifData=getExifData(filenameWithPath)

            conn=get_database_connection()
            cursor = conn.cursor ()
            ExifDataStr = json.dumps(ExifData)
            statement = f'''INSERT INTO photogallerydb.Photo (PhotoID, albumID, title, description, tags, photoURL, EXIF) VALUES ("{photoID}", "{albumID}", "{title}", "{description}", "{tags}", "{uploadedFileURL}", %s);'''
            
            result = cursor.execute(statement, (ExifDataStr,))
            conn.commit()
            conn.close()

        return redirect(f'''/album/{albumID}''')
    else:
        conn=get_database_connection()
        cursor = conn.cursor ()
        # Get title
        statement = f'''SELECT * FROM photogallerydb.Album WHERE albumID="{albumID}";'''
        cursor.execute(statement)
        albumMeta = cursor.fetchall()
        conn.close()

        return render_template('photoForm.html', albumID=albumID, albumName=albumMeta[0]['name'])



@app.route('/album/<string:albumID>/photo/<string:photoID>', methods=['GET'])
def view_photo(albumID, photoID):  
    """ photo page route.

    get:
        description: Endpoint to return a photo.
        responses: Returns a photo from a particular album.
    """ 
    conn=get_database_connection()
    cursor = conn.cursor ()

    # Get title
    statement = f'''SELECT * FROM photogallerydb.Album WHERE albumID="{albumID}";'''
    cursor.execute(statement)
    albumMeta = cursor.fetchall()

    statement = f'''SELECT * FROM photogallerydb.Photo WHERE albumID="{albumID}" and photoID="{photoID}";'''
    cursor.execute(statement)
    results = cursor.fetchall()
    conn.close()

    if len(results) > 0:
        photo={}
        photo['photoID'] = results[0]['photoID']
        photo['title'] = results[0]['title']
        photo['description'] = results[0]['description']
        photo['tags'] = results[0]['tags']
        photo['photoURL'] = results[0]['photoURL']
        photo['EXIF']=json.loads(results[0]['EXIF'])

        createdAt = datetime.strptime(str(results[0]['createdAt']), "%Y-%m-%d %H:%M:%S")
        updatedAt = datetime.strptime(str(results[0]['updatedAt']), "%Y-%m-%d %H:%M:%S")

        createdAt_UTC = timezone("UTC").localize(createdAt)
        updatedAt_UTC = timezone("UTC").localize(updatedAt)

        photo['createdAt']=createdAt_UTC.astimezone(timezone("US/Eastern")).strftime("%B %d, %Y")
        photo['updatedAt']=updatedAt_UTC.astimezone(timezone("US/Eastern")).strftime("%B %d, %Y")
        
        tags=photo['tags'].split(',')
        exifdata=photo['EXIF']
        
        return render_template('photodetail.html', photo=photo, tags=tags, exifdata=exifdata, albumID=albumID, albumName=albumMeta[0]['name'])
    else:
        return render_template('photodetail.html', photo={}, tags=[], exifdata={}, albumID=albumID, albumName="")



@app.route('/album/search', methods=['GET'])
def search_album_page():
    """ search album page route.

    get:
        description: Endpoint to return all the matching albums.
        responses: Returns all the albums based on a particular query.
    """ 
    query = request.args.get('query', None)

    conn=get_database_connection()
    cursor = conn.cursor ()
    statement = f'''SELECT * FROM photogallerydb.Album WHERE name LIKE '%{query}%' UNION SELECT * FROM photogallerydb.Album WHERE description LIKE '%{query}%';'''
    cursor.execute(statement)

    results = cursor.fetchall()
    conn.close()

    items=[]
    for item in results:
        album={}
        album['albumID'] = item['albumID']
        album['name'] = item['name']
        album['description'] = item['description']
        album['thumbnailURL'] = item['thumbnailURL']
        items.append(album)

    return render_template('searchAlbum.html', albums=items, searchquery=query)



@app.route('/album/<string:albumID>/search', methods=['GET'])
def search_photo_page(albumID):
    """ search photo page route.

    get:
        description: Endpoint to return all the matching photos.
        responses: Returns all the photos from an album based on a particular query.
    """ 
    query = request.args.get('query', None)

    conn=get_database_connection()
    cursor = conn.cursor ()
    statement = f'''SELECT * FROM photogallerydb.Photo WHERE title LIKE '%{query}%' AND albumID="{albumID}" UNION SELECT * FROM photogallerydb.Photo WHERE description LIKE '%{query}%' AND albumID="{albumID}" UNION SELECT * FROM photogallerydb.Photo WHERE tags LIKE '%{query}%' AND albumID="{albumID}" UNION SELECT * FROM photogallerydb.Photo WHERE EXIF LIKE '%{query}%' AND albumID="{albumID}";'''
    cursor.execute(statement)

    results = cursor.fetchall()
    conn.close()

    items=[]
    for item in results:
        photo={}
        photo['photoID'] = item['photoID']
        photo['albumID'] = item['albumID']
        photo['title'] = item['title']
        photo['description'] = item['description']
        photo['photoURL'] = item['photoURL']
        items.append(photo)

    return render_template('searchPhoto.html', photos=items, searchquery=query, albumID=albumID)



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
