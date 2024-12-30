import datetime
from operator import or_
from flask import Flask, render_template, request,url_for,redirect
from .models import *
from flask import current_app as app

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        usr=User_Info.query.filter_by(email=uname,password=pwd).first()
        service_professional = Service_Professional.query.filter_by(email=uname, password=pwd).first()
        if usr and usr.role==0:
            return redirect(url_for("admin_dashboard",user_msg=usr.fullname))
        elif usr and usr.role==1:
            if usr.status=="Blocked":
                return render_template("login.html",msg="your account has been blocked my admin")
            else:    
                return redirect(url_for("user_dashboard",user_msg=usr.fullname,user_id=usr.id))
        elif service_professional and service_professional.role==2:
            if service_professional.status=="Pending":
                return render_template("login.html",msg="wait for admin approval")
            elif service_professional.status=="Rejected":
                return render_template("login.html",msg="your application has been rejected")
            elif service_professional.status=="Blocked":
                return render_template("login.html",msg="your account has been blocked my admin")
            else:
                return redirect(url_for("professional_dashboard",user_msg=service_professional.fullname, prof_id=service_professional.id))
        else:
            return render_template("login.html",msg="Inavalid user credentials...")
    return render_template("login.html",msg="")
 
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        fullname=request.form.get("fullname")
        address=request.form.get("address")
        pincode=request.form.get("pincode")
        existing_user = User_Info.query.filter_by(email=uname).first()
        existing_professional = Service_Professional.query.filter_by(email=uname).first()
        if existing_user or existing_professional:
            return render_template("signup.html",msg="email already exists")
        new_usr=User_Info(email=uname,password=pwd,fullname=fullname,address=address,pincode=pincode)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now")
    return render_template("signup.html",msg="")

@app.route("/service_professional_signup", methods=["GET","POST"])
def service_professional_signup():
    service=get_service()
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        fullname=request.form.get("fullname")
        service_name=request.form.get("service_name")
        description=request.form.get("description")
        experience=request.form.get("experience")
        address=request.form.get("address")
        pincode=request.form.get("pincode")
        existing_user = User_Info.query.filter_by(email=uname).first()
        existing_professional = Service_Professional.query.filter_by(email=uname).first()
        if existing_user or existing_professional:
            return render_template("service_professional_signup.html",msg="email already exists")
        new_professional=Service_Professional(email=uname,password=pwd,fullname=fullname,address=address,pincode=pincode,experience=experience,service_name=service_name,description=description)
        db.session.add(new_professional)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now")
    return render_template("service_professional_signup.html",service=service,msg="")

@app.route("/admin/<user_msg>", methods=["GET","POST"])
def admin_dashboard(user_msg):
    users=get_users()
    service=get_service()
    service_professional=get_pending_professional()
    service_request=get_service_request()
    # service_request=Service_Request.query.filter_by(service_id=service_id).all()
    return render_template("admin_dashboard.html",user_msg=user_msg,users=users,service=service,service_professional=service_professional,service_request=service_request)

@app.route("/user/<user_msg>/<user_id>" , methods=["GET","POST"])
def user_dashboard(user_msg,user_id):
    if request.method=="GET":
        service=get_service()
        requests = Service_Request.query.filter_by(customer_id=user_id).all()
        return render_template("user_dashboard.html",user_msg=user_msg,service=service,service_requests=requests,user_id=user_id)
    return render_template("user_dashboard.html",user_msg=user_msg,service=service,service_requests=requests,user_id=user_id)    

@app.route("/professional/<user_msg>/<int:prof_id>")
def professional_dashboard(user_msg,prof_id):
    status = Service_Professional.query.filter_by(id=prof_id).first().status
    if status=="Blocked":
       return render_template("login.html")
    service_prof = Service_Professional.query.filter_by(id=prof_id).first().service_name
    
    # service_prof_name = Service_Professional.query.filter_by(id=prof_id).first().fullname
    service_id=Service.query.filter_by(service_name=service_prof).first().id
    service_request=Service_Request.query.filter_by(service_id=service_id).all()
    # filter_prof_id=Service_Request.query.filter_by(professional_id=prof_id).all()
    # print(service_prof)
    return render_template("professional_dashboard.html",user_msg=user_msg,prof_id=prof_id,service_request=service_request,service_id=service_id)


@app.route("/service/<user_msg>", methods=["GET","POST"])
def add_service(user_msg):
    if request.method=="POST":
        sname=request.form.get("service_name")
        description=request.form.get("description")
        base_price=request.form.get("base_price")
        time_required=request.form.get("time_required")
        new_service=Service(service_name=sname,description=description,base_price=base_price,time_required=time_required)
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for("admin_dashboard",user_msg=user_msg,))
        
    return render_template("add_service.html",user_msg=user_msg)

@app.route("/book_service/<user_msg>/<int:service_id>/<int:user_id>", methods=["GET","POST"])
def book_service(user_msg,service_id, user_id):
    # Create a new service request
    services=filter_service(service_id)
    service_name=services.service_name
    service=Service_Professional.query.filter_by(service_name=service_name).all()
    if service:
        if request.method=="POST":
            new_request = Service_Request(
                service_id=service_id,
                customer_id=user_id,
                date_of_request=datetime.date.today(),
                status="Requested",
                description=request.form.get("description")
            )
            db.session.add(new_request)
            db.session.commit()
            return redirect(url_for("user_dashboard", user_id=user_id,user_msg=user_msg))
        return render_template("book_service.html", user_id=user_id,user_msg=user_msg,service_id=service_id,services=services)
    
    else:
        return render_template("msg.html",msg="service not available")

@app.route("/service_requests_accept/<user_msg>/<prof_id>/<req_id>", methods=["GET", "POST"])
def service_requests_accept(user_msg,prof_id,req_id):
    service_requests=Service_Request.query.get(req_id)
    if service_requests:
        if request.method=="GET":
            if service_requests.status=='Requested':
                service_requests.status='Accepted'
            elif service_requests.status=='Rejected':
                return render_template("msg.html",msg="Request Already Rejected")  
            else:
                return render_template("msg.html",msg="Request Already Accepted")  
        service_requests.professional_id = prof_id
        db.session.commit()     
        return redirect(url_for("professional_dashboard",user_msg=user_msg, prof_id=prof_id,req_id=req_id))
    return redirect(url_for("professional_dashboard",user_msg=user_msg, prof_id=prof_id,req_id=req_id))

@app.route("/service_requests_reject/<user_msg>/<prof_id>/<req_id>", methods=["GET", "POST"])
def service_requests_reject(user_msg,prof_id,req_id):
    service_requests=Service_Request.query.get(req_id)
    if service_requests:
        if service_requests.status=='Requested':
            service_requests.status='Rejected'
        service_requests.professional_id = prof_id    
        db.session.commit()      
    return redirect(url_for("professional_dashboard",user_msg=user_msg, prof_id=prof_id,req_id=req_id)) 


@app.route("/edit_request/<user_msg>/<req_id>/<user_id>", methods=["GET", "POST"])
def edit_request(req_id, user_id, user_msg):
    request_obj = Service_Request.query.get(req_id)
    if request.method == "POST":
        new_description = request.form.get("description")
        new_status = request.form.get("status")
        if new_description:
            request_obj.description = new_description
        else:
            request_obj.description = request_obj.description
        if new_status:
            request_obj.status = new_status
        db.session.commit()
        return redirect(url_for("user_dashboard", user_msg=user_msg, user_id=user_id,req_id=req_id))
    return render_template("edit_request.html", request=request_obj, user_id=user_id, user_msg=user_msg,req_id=req_id)



@app.route("/review_service/<user_msg>/<req_id>/<user_id>", methods=["GET", "POST"])
def review_service(req_id, user_id,user_msg):
    request_obj = Service_Request.query.get(req_id)
    if request.method == "POST":
        request_obj.status = "Closed"
        request_obj.date_of_completion=datetime.date.today()
        existing_review = Review.query.filter_by(request_id=req_id).first()
        if existing_review:
            return redirect(url_for("user_dashboard",user_msg=user_msg, user_id=user_id))

        rating = request.form.get("rating")
        description = request.form.get("description")

        new_review = Review(
            customer_id=user_id,
            professional_id=request.form.get("professional_id"),
            request_id=req_id,
            rating=rating,
            description=description
            
        )
        
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for("user_dashboard",user_msg=user_msg, user_id=user_id))

    request_obj = Service_Request.query.get(req_id)
    return render_template("review_service.html", request=request_obj, user_id=user_id,user_msg=user_msg)


@app.route("/view_service/<ser_id>/<user_msg>", methods=["GET","POST"])
def view_service(user_msg,ser_id):
    service=Service.query.get(ser_id)
    return render_template("view_service.html", service=service,user_msg=user_msg)

@app.route("/view_professional/<prof_id>/<user_msg>", methods=["GET","POST"])
def view_professional(user_msg,prof_id):
    prof=Service_Professional.query.get(prof_id)
    return render_template("view_professional.html", prof=prof,user_msg=user_msg)

@app.route("/professional_profile/<user_msg>/<prof_id>", methods=["GET","POST"])
def professional_profile(user_msg,prof_id):
    prof=Service_Professional.query.get(prof_id)
    if request.method == "POST":
        prof.fullname=request.form.get("fullname")
        prof.email=request.form.get("email")
        prof.password=request.form.get("password")
        prof.service_name=request.form.get("service_name")
        prof.address=request.form.get("address")
        prof.description=request.form.get("description")
        prof.pincode=request.form.get("pincode")
        prof.experience=request.form.get("experience")
        db.session.commit()
        return redirect(url_for("professional_dashboard",user_msg=user_msg,prof_id=prof_id))
    return render_template("professional_profile.html", prof=prof,user_msg=user_msg)

@app.route("/user_profile/<user_id>/<user_msg>", methods=["GET","POST"])
def user_profile(user_msg,user_id):
    user=User_Info.query.get(user_id)
    if request.method == "POST":
        user.fullname=request.form.get("fullname")
        user.email=request.form.get("email")
        user.password=request.form.get("password")
        user.address=request.form.get("address")
        user.pincode=request.form.get("pincode")
        db.session.commit()
        return redirect(url_for("user_dashboard",user_msg=user_msg,user_id=user_id))
        
    return render_template("user_profile.html", user=user,user_msg=user_msg,user_id=user_id)

@app.route("/service_requests/<prof_id>/<user_msg>", methods=["GET","POST"])
def service_requests(user_msg,prof_id):
    if request.method == "GET":
        requests = Review.query.filter_by(professional_id=prof_id).all()
        return render_template("service_requests.html",user_msg=user_msg,prof_id=prof_id,service_requests=requests)


@app.route("/apsearch/<user_msg>", methods=["GET","POST"]) 
def apsearch(user_msg):
    # print("inside search")
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        
        # role = request.args.get('role')

        by_professional=search_by_professional(search_txt)
        # if by_professional:
        # if role == 'admin':
        #     return render_template("admin_dashboard.html",user_msg=user_msg, service_professional=by_professional)
        # if by_service:
        # if role == 'admin':
        return render_template("view_prof.html",user_msg=user_msg,service_professional=by_professional)
        # if role == 'user':
        #     return render_template("user_dashboard.html",user_msg=user_msg, service=by_service,pincode=by_pincode,location=by_location)

    return redirect(url_for("view_prof",user_msg=user_msg))

@app.route("/ausearch/<user_msg>", methods=["GET","POST"])
def ausearch(user_msg):
    # print("inside search")
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        
        by_user=search_by_user(search_txt)
        return render_template("view_user.html",user_msg=user_msg,users=by_user)

    return redirect(url_for("view_user",user_msg=user_msg))

@app.route("/usearch/<user_msg>/<user_id>", methods=["GET","POST"])
def usearch(user_msg,user_id):
    if request.method=="POST":
        search_txt=request.form.get("search_txt")

        service=search_by_service(search_txt)
        location=search_by_location(search_txt)
        by_location=search_by_service(location)
        pincode=search_by_pincode(search_txt)
        by_pincode=search_by_service(pincode)
        print("by_pincode",pincode) 
        
        if service:
            by_service=service
            print("service",by_service)            
        elif by_location:
            by_service=by_location
            print("by_location",by_service)
        elif by_pincode:
            by_service=by_pincode
            print("by_pincode",by_service)  
        else: return render_template("user_dashboard.html",user_msg=user_msg,user_id=user_id)
        
        return render_template("user_dashboard.html",user_msg=user_msg,user_id=user_id, service=by_service)

    return redirect(url_for("user_dashboard",user_msg=user_msg,user_id=user_id))

@app.route("/view_user/<user_msg>", methods=["GET","POST"])
def view_user(user_msg):
    # print("inside view user")
    if request.method=="GET":
        # print("inside view user get")
        users=get_users()
        # print(users)
        return render_template("view_user.html",user_msg=user_msg,users=users)
        
    return render_template("view_user.html",user_msg=user_msg)

@app.route("/view_prof/<user_msg>", methods=["GET","POST"])
def view_prof(user_msg):
    # print("inside view prof")
    if request.method=="GET":
        # print("inside view prof get")
        service_professional=get_active_professional()
        # print(service_professional)
        return render_template("view_prof.html",user_msg=user_msg,service_professional=service_professional)
        
    return render_template("view_prof",user_msg=user_msg,service_professional=service_professional)

@app.route("/change_status/<user_id>/<user_msg>", methods=["GET","POST"])
def user_status(user_msg,user_id):
    print("inside view user")
    user_status=User_Info.query.get(user_id)
    if user_status:
        if user_status.status == "Active":
            user_status.status = "Blocked"
        elif user_status.status == "Blocked":
            user_status.status = "Active"
        db.session.commit()
    return redirect(url_for("view_user",user_msg=user_msg))

@app.route("/approve_status/<prof_id>/<user_msg>", methods=["GET","POST"])
def professional_status(user_msg,prof_id):
    print("inside view prof")
    professional_status=Service_Professional.query.get(prof_id)
    if professional_status:
        if professional_status.status == "Pending":
            professional_status.status = "Active"
            db.session.commit()
            return redirect(url_for("admin_dashboard",user_msg=user_msg))
        elif professional_status.status == "Active":
            professional_status.status = "Blocked"
        elif professional_status.status == "Blocked":
            professional_status.status = "Active"
        db.session.commit()
    return redirect(url_for("view_prof",user_msg=user_msg))


@app.route("/reject_status/<prof_id>/<user_msg>", methods=["GET","POST"])
def reject_status(user_msg,prof_id):
    print("inside view prof")
    professional_status=Service_Professional.query.get(prof_id)
    if professional_status:
        if professional_status.status == "Pending":
            professional_status.status = "Rejected"
        db.session.delete(professional_status)
        db.session.commit()
    return redirect(url_for("admin_dashboard",user_msg=user_msg))

@app.route("/edit_service/<ser_id>/<user_msg>", methods=["GET","POST"])
def edit_service(user_msg,ser_id):
    print("inside view user")
    edit_service=Service.query.get(ser_id)
    if request.method=="POST":
        sname=request.form.get("service_name")
        sprice=request.form.get("base_price")
        stime=request.form.get("time_required")
        sdescription=request.form.get("description")
        edit_service.service_name=sname
        edit_service.base_price=sprice
        edit_service.time_required=stime
        edit_service.description=sdescription
        db.session.commit()
        return redirect(url_for("admin_dashboard",user_msg=user_msg))
    return render_template("edit_service.html",service=edit_service,user_msg=user_msg)

@app.route("/delete_service/<ser_id>/<user_msg>", methods=["GET","POST"])
def delete_service(user_msg,ser_id):
    edit_service=Service.query.get(ser_id)
    db.session.delete(edit_service)
    db.session.commit()
    return redirect(url_for("admin_dashboard",user_msg=user_msg))

def get_service():
    service=Service.query.all()
    return service


def filter_service(service_id):
    service=Service.query.filter_by(id=service_id).first()
    return service

def get_users():
    users=User_Info.query.all()
    return users

def service_professional():
    service_professional=Service_Professional.query.all()
    return service_professional

def get_active_professional():
    print("inside get_professional")
    service_professional=Service_Professional.query.filter(or_(
        Service_Professional.status.ilike("%active%"),
        Service_Professional.status.ilike("%blocked%")
        )).all()
    # print(service_professional)
    return service_professional

def get_pending_professional():
    # print("inside get_pending_professional")
    service_professional=Service_Professional.query.filter(Service_Professional.status.ilike("%pending%")).all()
    # print(service_professional)
    return service_professional

def get_service_request_by_id(service_name):
    service_request=Service_Request.query.filter(Service_Request.service_name.ilike(f"%{service_name}%")).all()
    return service_request

def get_service_request():
    service_request=Service_Request.query.all()
    return service_request


def search_by_service(search_txt):
        services=Service.query.filter(Service.service_name.ilike(f"%{search_txt}%")).all()
        return services
def search_by_location(search_txt):
        location=Service_Professional.query.filter(Service_Professional.address.ilike(f"%{search_txt}%")).all()
        for id in location:
            return id.service_name
def search_by_pincode(search_txt):
        pincode=Service_Professional.query.filter(Service_Professional.pincode.ilike(f"%{search_txt}%")).all()
        for pin in pincode:
            print("pin",pin.service_name)
            return pin.service_name
def search_by_professional(search_txt):
        fullname=Service_Professional.query.filter(Service_Professional.fullname.ilike(f"%{search_txt}%")).all()
        return fullname
def search_by_user(search_txt):
        user=User_Info.query.filter(User_Info.fullname.ilike(f"%{search_txt}%")).all()
        return user