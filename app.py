from flask import Flask, render_template, request, redirect
import pymongo
from pymongo import MongoClient

from flask_bcrypt import Bcrypt
from simplecrypt import encrypt,decrypt
from cryptography.fernet import Fernet



cluster = MongoClient("mongodb+srv://aravinth:aravinth@cluster0.riij8.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["test"]
login = db["login"]
collection = db["password"]
app = Flask(__name__)
bcrypt = Bcrypt(app)

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        names = request.form["name"]
        password = request.form["password"]
        con_password = request.form["con_password"]
        if(password != con_password):
            return render_template("register.html",msg="password and confirm password must not be same")
        detail = login.find({"name":names})
        a=''
        for i in detail:
            a=i
            break
        if a:
             return render_template("register.html",msg="username already present")
        pw_hash = bcrypt.generate_password_hash(password)
        key = Fernet.generate_key()
        login.insert_one({"name":names,"password":pw_hash.decode(),"key":key.decode()})
        
        return render_template("register.html",msg="registered success")
    return render_template("register.html")


@app.route('/',methods=["GET","POST"])
def hello():
    if request.method=="POST":
        names = request.form["name"]
        password = request.form["password"]
       
        
        
        if names:
            
            detail = login.find({"name":names})
            for i in detail:
                a = i
                break
           
            p=bytes(a["password"],"utf-8")
                   
            
            check = bcrypt.check_password_hash(p, password)
            if not check:
                return render_template("index.html",msg="password incorrect")
            return render_template("home.html",name=names)
        return render_template("index.html",msg="no users found")

    return render_template('index.html')
@app.route('/find',methods = ['POST'])
def add():
    if request.method=="POST":
        names = request.form["name"]
        password = request.form["password"]
        cname = request.form["cname"]
        cpass = request.form["cpass"]
        
        isfind = collection.find({"name":names})
        s=""
        logcheck = login.find({"name":names})
        for i in logcheck:
            a=i
            break

        p = bytes(a["password"],"utf-8")
        check = bcrypt.check_password_hash(p,password)
        if not check:
            return render_template("home.html",name=names,msg="your secret credential not matching ")
        k=a["key"]+password
        print(k)
        k=k.encode()
        f=Fernet(k)
        cpass = f.encrypt(cpass.encode())
        cpass=cpass.decode()
        




        for i in isfind:
            s=i
            break

        if not s:
            d_cname=[]
            d_cpass=[]
            d_cname.append(cname)
            d_cpass.append(cpass)
            collection.insert_one({"name":names,"cname":d_cname,"cpass":d_cpass})
            return "inserted"
        d_cname = s["cname"]
        d_cname.append(cname)
        d_cpass = s["cpass"]
        d_cpass.append(cpass)
        collection.update_one({"name":names},{"$set":{"cname":d_cname,"cpass":d_cpass}})

        return render_template("home.html",name=names,msg="password added to vault")

@app.route('/getall',methods = ['POST'])
def showall():
    if request.method=="POST":
          names = request.form["name"]
          password = request.form["password"]
          logcheck = login.find({"name":names})
          for i in logcheck:
            a=i
            break

          p = bytes(a["password"],"utf-8")
          check = bcrypt.check_password_hash(p,password)
          
          isfind = collection.find({"name":names})
          s=""
          for i in isfind:
              s=i
              break
          if not check:
              cd_pass=[]
              for i in range(len(s["cname"])):
                  cd_pass.append(s["cpass"][i])
              return render_template("home.html",name=names,passwords = s,password=cd_pass)
          if s:
              k=a["key"]+password
              k=k.encode()
              f=Fernet(k)
              cpass=[]
              print()
              



              for i in range(len(s["cname"])):
                  p=f.decrypt(s["cpass"][i].encode("utf-8"))
                  cpass.append(p.decode())
          
             


                    

              
              return render_template("home.html",name=names,passwords = s,password=cpass)
          return render_template("home.html",name=names)

          







if __name__ == "__main__":

    app.run(debug=True)
