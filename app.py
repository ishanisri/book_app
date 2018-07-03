from flask import render_template,redirect, request, flash,g,session,url_for,Flask

import sqlite3 as sql
from werkzeug import generate_password_hash, check_password_hash
import requests
import simplejson as json

app = Flask(__name__)
app.secret_key="why would i tell my secret key?"


from flask import g

DATABASE = '/path/to/books.db'
  




@app.route("/")
def main():
    return render_template('index.html')
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html') 
@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html') 

@app.route('/signUp',methods=['GET','POST'])
def signedUp():
    if(request.method=='POST'):
        username= request.form.get('inputName')
        email = request.form.get('inputEmail')
        password=request.form.get('inputPassword')
        
        print(username+" "+email+" "+password)
        hashed_password = generate_password_hash(password)
        print(hashed_password)
        
        print("hi")	
        
        with sql.connect("books.db") as con:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS account_holder(user_email TEXT DEFAULT NULL,username TEXT NOT NULL PRIMARY KEY,password TEXT DEFAULT NULL)")
            cur.execute("INSERT INTO account_holder (user_email,username,password) VALUES (?,?,?)", (email,username,hashed_password))
            cur.execute("CREATE TABLE IF NOT EXISTS books( title TEXT DEFAULT NULL, subtitle DEFAULT NULL,author TEXT DEFAULT NULL,isbn TEXT DEFAULT NULL,subject TEXT DEFAULT NULL,publisher TEXT DEFAULT NULL,image TEXT DEFAULT NULL) ")
            cur.execute("CREATE TABLE IF NOT EXISTS favourite_books(user TEXT DEFAULT NULL,title TEXT DEFAULT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS currently_reading_books(user TEXT DEFAULT NULL,title TEXT DEFAULT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS read_books(user TEXT DEFAULT NULL,title TEXT DEFAULT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS want_to_read_books(user TEXT DEFAULT NULL,title TEXT DEFAULT NULL)")
            cur.execute("CREATE TABLE IF NOT EXISTS library(user TEXT DEFAULT NULL,title TEXT DEFAULT NULL)")
            
            r=requests.get('https://www.googleapis.com/books/v1/volumes?q=""&maxResults=40&apikey=AIzaSyBFQUNN6aGFMoWgfzLEvrBC6750DO_w1g8')
            
            for i in r.json()['items']:
            	_title=i['volumeInfo']['title']
            	_subtitle=i['volumeInfo'].get('subtitle','')

            	
            	_author=','.join(i['volumeInfo'].get('authors',''))
            	print(_author)  
            	_publisher=i['volumeInfo'].get('publisher','')
            	_subject=','.join(i['volumeInfo'].get('categories',''))

            	print(_subject)
            	_image=None
            	_isbn=None
            	check=i['volumeInfo']['industryIdentifiers']
            	print(check)
            	for val in check:
            	 val1=val.get('type')
            	 print(val1)
            	 if (val1 =='ISBN_13'):
            	    _isbn=val['identifier']
            	    print(_isbn)
            	if i['volumeInfo'].get('imageLinks') is not None:
            		_image=i['volumeInfo'].get('imageLinks').get('thumbnail')
            	print(_image)
            	cur.execute("SELECT * FROM books where title=?",(_title,))
            	data=cur.fetchall()
            	if(data):
            		print("books not empty")
            	else:	
            		cur.execute("INSERT INTO books(title,subtitle,author,subject,publisher,image,isbn) VALUES (?,?,?,?,?,?,?)",(_title,_subtitle,_author,_subject,_publisher,_image,_isbn))
            	print(_isbn)
             


            
            cur.execute("SELECT * FROM account_holder where username=?",(username,))
            data=cur.fetchall()
            print(data)
            con.commit()

                                                                                         
        session['user']=username

        
 
           
    return redirect('/userHome') 


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')


@app.route('/validateLogin',methods=['GET','POST'])
def validateLogin():
	if(request.method=='POST'):
	    con = sql.connect("books.db")
	    cur=con.cursor()
	    
	    try:
	        
	        username = request.form['inputName']
	        password = request.form['inputPassword']
	        cur.execute("SELECT * FROM account_holder where username=?",(username,))
	        print("hi")
	        data = cur.fetchall()
	        print(data)
	        if len(data) > 0:

	            if check_password_hash(str(data[0][2]),password):
	                print("inside check")
	                session['user'] = data[0][1]
	                
	            else:
	                return render_template('error.html',error = 'Wrong Email address or Password.')
	        else:
	            return render_template('error.html',error = 'Wrong Email address or Password!!!!')                  

	 
	    except Exception as e:
	        return render_template('error.html',error = str(e))
	    finally:
	        cur.close()
	        con.close()
	return redirect('/userHome')  

@app.route('/userHome')
def userHome():
	con = sql.connect("books.db")
	cur=con.cursor()
	_username=session.get('user')
	cur.execute("SELECT * FROM books ")
	data=cur.fetchall()
	data_dict=[]
	i=0
	for x in data:
		x_dict={
		       'Title':x[0],
		       'Subtitle':x[1],
		       'Author':x[2],
		       'Subject':x[4],
		       'Publisher':x[5],
		       'url':x[6],
		       'ISBN':x[3],
		        'i':i
		}
		i=i+1
		data_dict.append(x_dict)
	print(data_dict)		
	cur.execute("SELECT * FROM currently_reading_books WHERE user=? ",(_username,))
	dat=cur.fetchall()
	print("dat")
	print(dat)
	cur_dict=[]
	for work in dat:
		current={
		  'Title':work[1],

		}
		cur_dict.append(current)

	print(cur_dict)
	cur.execute("SELECT * FROM favourite_books WHERE user=? ",(_username,))
	dat=cur.fetchall()
	print("dat")
	print(dat)
	fav_dict=[]
	for work in dat:
		fav={
		  'Title':work[1],

		}
		fav_dict.append(fav)

	print(fav_dict)
	

	cur.execute("SELECT * FROM want_to_read_books WHERE user=? ",(_username,))
	dat=cur.fetchall()
	print("dat")
	print(dat)
	want_dict=[]
	for work in dat:
		fav={
		  'Title':work[1],

		}
		want_dict.append(fav)

	print(want_dict)
	cur.execute("SELECT * FROM library WHERE user=? ",(_username,))
	dat=cur.fetchall()
	print("dat")
	print(dat)
	lib_dict=[]
	for work in dat:
		fav={
		  'Title':work[1],

		}
		lib_dict.append(fav)

	print(lib_dict)
	print("almost done")
	
	return render_template('userHome.html',data_dict=data_dict,cur_dict=cur_dict,fav_dict=fav_dict,want_dict=want_dict,lib_dict=lib_dict)

											



@app.route('/currently',methods=['POST'])
def show_currently_reading():

	con=sql.connect("books.db")
	cur=con.cursor()
	print("inside currently read")
	_username=session.get('user')
	r=request.json
	retrieved=json.dumps(r)
	print(r)
	cur.execute("SELECT * FROM currently_reading_books WHERE user=? and title=?",(_username,r))
	data=cur.fetchall()
	if(data):
	 print('not empty')
	else:
	 cur.execute("INSERT INTO currently_reading_books VALUES(?,?)",(_username,r))
	  
	con.commit()
	cur.close()
	con.close()
	
	return redirect('/userHome')

@app.route('/library',methods=['POST'])
def show_library():

	con=sql.connect("books.db")
	cur=con.cursor()
	print("inside library")
	_username=session.get('user')
	r=request.json
	retrieved=json.dumps(r)
	print(r)
	cur.execute("SELECT * FROM library WHERE user=? and title=?",(_username,r))
	data=cur.fetchall()
	if(data):
	 print('not empty')
	else:
	 cur.execute("INSERT INTO library VALUES(?,?)",(_username,r))
	  
	con.commit()
	cur.close()
	con.close()
	#print(request.referrer)
	return redirect('/userHome')

@app.route('/favourites',methods=['POST'])
def show_favourites():

	con=sql.connect("books.db")
	cur=con.cursor()
	print("inside favourites")
	_username=session.get('user')
	r=request.json
	retrieved=json.dumps(r)
	print(r)
	cur.execute("SELECT * FROM favourite_books WHERE user=? and title=?",(_username,r))
	data=cur.fetchall()
	if(data):
	 print('not empty')
	else:
	 cur.execute("INSERT INTO favourite_books VALUES(?,?)",(_username,r))
	  
	con.commit()
	cur.close()
	con.close()
	#print(request.referrer)
	return redirect('/userHome')


@app.route('/want',methods=['POST'])
def show_want():

	con=sql.connect("books.db")
	cur=con.cursor()
	print("inside want")
	_username=session.get('user')
	r=request.json
	retrieved=json.dumps(r)
	print(r)
	cur.execute("SELECT * FROM want_to_read_books WHERE user=? and title=?",(_username,r))
	data=cur.fetchall()
	if(data):
	 print('not empty')
	else:
	 cur.execute("INSERT INTO want_to_read_books VALUES(?,?)",(_username,r))
	  
	con.commit()
	cur.close()
	con.close()
	#print(request.referrer)
	print("hello")
	return redirect('/userHome')


@app.route('/search',methods=['GET','POST'])
def search():
	if (request.method=='POST'):
		print("hi")
		_query=request.form.get('radio',False)
		_param=request.form.get('search',False)
		print(_param)
		print(_query)
		
		_username=session.get('user')
		con=sql.connect("books.db")
		cur=con.cursor()
		if _query=='Title':
		   cur.execute("SELECT * FROM books WHERE title=?",(_param,))
		elif _query=='Author':
		   cur.execute("SELECT * FROM books WHERE  author=?",(_param,))
		elif _query=='Publisher':
		   cur.execute("SELECT * FROM books WHERE publisher=?",(_param,))
		elif _query=='Subject' :
		    print("inside")
		    cur.execute("SELECT * FROM books WHERE  subject=?",(_param,))
		    m=cur.fetchall()
		    print(m)
		elif _query=='ISBN':
		    cur.execute("SELECT * FROM books WHERE isbn=?",(_param,)) 
		data=cur.fetchall()
		print(data)
		i=0
		data_dict=[]
		if (data):
		 for x in data:
		   x_dict={
			       'Title':x[0],
			       'Subtitle':x[1],
			       'Author':x[2],
			       'Subject':x[4],
			       'Publisher':x[5],
			       'url':x[6],
			        'i':i
			}
		   i=i+1
		   data_dict.append(x_dict)
		 print(data_dict)
		 return render_template('searchPage.html',data_dict=data_dict)
		else: 
		 return render_template('error.html',error="No results found")
				      



if __name__ == "__main__":
     app.run(debug=True)  