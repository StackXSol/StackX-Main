from datetime import datetime
from heapq import merge
from mimetypes import init
from random import Random
import random
from sqlite3 import Date
from turtle import pd
from flask import Flask, redirect,render_template,request, session
import smtplib
import firebase_admin
from flask_session import Session
from firebase_admin import firestore,credentials, storage

from fpdf import FPDF

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


cred = credentials.Certificate('firebase.json')
firebase_db = firebase_admin.initialize_app(cred,{
  'projectId': 'stackx-24edc',
  'storageBucket': 'stackx-24edc.appspot.com'
})
db = firestore.client()


def generateOL(id, name, start, end, stipend, till, field):
    class PDF(FPDF):
        def header(self):
            # Logo
            self.image('StackX.png', 10, 8, 18)
            # Arial bold 15
            self.set_font('Times', 'B', 15)
            # Move to the right
            self.cell(80)
            # Title
            self.cell(30, 10, 'Internship Offer Letter', 0, 0, 'C')
            self.set_font('Times', 'I', 12)
            self.cell(130, 10, 'EMP ID: {0}'.format(id), 0, 0, 'C')
            # Line break
            self.ln(25)

        # Page footer
        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-35)
            self.image('sign.png',10,180,50,40)
            self.set_y(-15)
            # Arial italic 8
            self.set_font('Arial', 'I', 8)      
            self.cell(0, 10, '' + "stackxsolutions.in", 0, 0, 'C')
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', 'B', 15)   
    pdf.cell(2,10,"{0},".format(name),0,1)   
    pdf.set_font('Times', '', 14) 
    pdf.multi_cell(h=6.0, align='L', w=0, txt="We are pleased to offer you an internship at our company as {0} Developer. Your internship shall commence from {1} and shall end on {2} ('Term'). The terms and conditions of your internship with the company are set forth below:".format(field,start,end), border=0)
    pdf.multi_cell(h=4.0, align='L', w=0, txt="", border=0)   
    pdf.set_font('Times', '', 12)
    pdf.cell(2,10,"",0,0)    
    pdf.multi_cell(h=6.0, align='L', w=0, txt="1. Subject to your acceptance of the terms and conditions contained herein, your project and responsibilities during the Term will be determined by the supervisor assigned to you for the duration of the internship.", border=0)    
    pdf.cell(2,10,"",0,0)
    pdf.multi_cell(h=6.0, align='L', w=0, txt="2. You are eligible for a fixed stipend of Rs. {0}/- during the term which shall be paid monthly on completion of the tasks assigned to you during your internship to the satisfaction of the company.".format(stipend), border=0)
    pdf.cell(2,10,"",0,0)
    pdf.multi_cell(h=6.0, align='L', w=0, txt="3. Incentives depending on the project will be paid in surplus to the fixed stipend.", border=0)
    pdf.cell(2,10,"",0,0)
    pdf.multi_cell(h=6.0, align='L', w=0, txt="4. Your timings of work can differ depending on the project assigned, Monday to Saturday.", border=0)
    pdf.cell(2,10,"",0,0)
    pdf.multi_cell(h=6.0, align='L', w=0, txt="5. If company finds your work way below the expected quality then company holds full power to terminate your internship.", border=0)
    pdf.cell(2,10,"",0,0)
    pdf.multi_cell(h=6.0, align='L', w=0, txt="6. You will sign a confidentiality agreement with the company before you commence your internship.", border=0)
    pdf.cell(2,10,"",0,0)
    pdf.multi_cell(h=6.0, align='L', w=0, txt="7. The internship cannot be constructed as an employment or an offer of employment with StackX.", border=0)
    pdf.multi_cell(h=4.0, align='L', w=0, txt="", border=0)   
    pdf.set_font('Times', '', 14)
    pdf.multi_cell(h=6.0, align='L', w=0, txt="Please confirm your acceptance of the terms of this offer by {0} failing which, we have the right to cancel the internship. We look forward to having you on our team! If you have any questions, please feel free to reach out to us.".format(till), border=0)
    pdf.output('pdfs/IOL.pdf', 'F')

host_mail = "mail.stackx.online"
sender_email = "info@stackx.online"
email_pass = "StackX@123"

def send_email(user, pwd, recipient, subject, body):   
    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body
    
    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    with smtplib.SMTP_SSL(host=host_mail) as smtp:
        smtp.login(user,pwd)
        smtp.sendmail(user,TO,message)
        smtp.quit()
    

@app.route("/")

def index():
    return render_template("index.html")

@app.route("/apps")
def apps():
    return render_template("apps.html")

@app.route("/games")
def games():
    return render_template("games.html")

@app.route("/about_us")
def about():
    return render_template("about.html")

@app.route("/joinus")
def join():
    return render_template("join.html")

@app.route("/ping", methods=["POST"])
def send_query():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]
    try:
        send_email(sender_email,email_pass,"stackx1617@gmail.com",name,f"From {email} \nMessage is:\n{message}")
        send_email(sender_email,email_pass,email,name,f"Thank You for contacting us.\nTeam Stackx")

    except Exception as e:
        print(e)
        return redirect("/")
    return redirect("/")

#admin Url's 

@app.route("/admin")
def admin():
    return render_template("Admin/login.html")

@app.route("/adminlogin", methods=["POST"])
def admin_login():
    email = request.form["email"]
    password = request.form["password"]
    if(email=="stackx1617@gmail.com" and password=="StackX"):
        session["auth"] = True
        return render_template("Admin/homePage.html")
    else:
       return redirect("/admin")

@app.route("/admin/add", methods=["POST"])
def admin_add():    
    return render_template("Admin/addEmployee.html")

@app.route("/admin/add/employee", methods=["POST"])
def add_employee():  
    email = request.form["email"]
    name = request.form["name"]    
    start = request.form["start"]
    end = request.form["end"]
    till = request.form["till"]
    field = request.form["field"]
    stipend = request.form["stipend"]
    id = random.randint(1000000, 9999999)  
    generateOL(str(id),name,start,end,stipend,till,field)
    bucket = storage.bucket()     
    blob = bucket.blob(str(id))
    blob.upload_from_filename("./pdfs/IOL.pdf")
    blob.make_public()
    db.collection("EmployeeID").document(str(id)).set({"currentProject": "No Project", "empId":str(id),"incentivePaid":str(0),"internshipEnd":str(end),"internshipStart":str(start),"internshipofferLetter":blob.public_url,"name":str(name),"paidStipened":str(0),"stipened":stipend,"email":email,"timePeriod":str(Date.today()),"unpaidStipened":str(int(stipend)*3),"projectDone":[]},merge=True)
    return redirect("/admin")

@app.route("/admin/manage")
def employees():   
    if(session.get("auth")==True):
        employees = []
        for i in db.collection("EmployeeID").get():
            employees.append(i.to_dict())
        return render_template("Admin/employees.html", collection = employees)
    return redirect("/admin")

@app.route("/admin/manage/<empid>")
def manageEmployee(empid):   
    if(session.get("auth")==True):
        key = db.collection("EmployeeID").document(empid).get()
        data = key.to_dict()        
        data_set = {"empid":data["empId"],"stipend":data["stipened"],"incentives":data["incentivePaid"],"status":"Active", "Name":data["name"]}
        return render_template("Admin/employeeDash.html", data = data_set, projects = data["projectDone"])
    return redirect("/admin")

#employee funcs

@app.route("/admin/addstipend/<empid>/<stipend>")
def addStipend(empid,stipend):
    if(session.get("auth")==True):
        key = db.collection("EmployeeID").document(empid).get()
        data = key.to_dict()
        if(int(data["unpaidStipened"])>=int(stipend)):
            new_bal = int(data["paidStipened"])+int(stipend)
            new_left = int(data["unpaidStipened"])-int(stipend)
            db.collection("EmployeeID").document(empid).set({"paidStipened": new_bal,"unpaidStipened":new_left},merge=True)
        return redirect("/admin/manage/{0}".format(empid))
    return redirect("/admin")

@app.route("/admin/addincentive/<empid>/<incentive>")
def addIncentive(empid,incentive):    
    if(session.get("auth")==True):
        key = db.collection("EmployeeID").document(empid).get()
        data = key.to_dict()        
        new_bal = int(data["incentivePaid"])+int(incentive)            
        db.collection("EmployeeID").document(empid).set({"incentivePaid": new_bal},merge=True)
        return redirect("/admin/manage/{0}".format(empid))
    return redirect("/admin")

@app.route("/admin/assignProject/<empid>", methods=["POST"])
def assignProject(empid):
    if(session.get("auth")):
        key = db.collection("EmployeeID").document(empid).get()
        data = key.to_dict()  
        previous_project = {"projectName": data["currentProject"], "timePeriod":data["timePeriod"]}
        project = request.form["project"]
        deadline = request.form["deadline"]
        db.collection("EmployeeID").document(empid).update({"projectDone":firestore.ArrayUnion([previous_project])})
        db.collection("EmployeeID").document(empid).set({"currentProject":project, "timePeriod":deadline},merge=True)
        return redirect("/admin/manage/{0}".format(empid))
    return redirect("/admin")

    
    
    


if __name__ == '__main__':
    app.run(debug=True)