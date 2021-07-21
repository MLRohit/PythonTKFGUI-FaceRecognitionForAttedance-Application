
import tkinter
from tkinter import *
import tkinter.messagebox as tmsg
from tkinter import ttk
import tkinter.simpledialog as tsd
from PIL import Image, ImageTk
import pandas as pd
import numpy as np
import csv
import cv2
import datetime
import time
import os
import pyrebase

# firebase authentication connection
firebaseConfig = {
    'apiKey': "AIzaSyDxDPLXTKUe464xyKbsBm20vBzdEl4aCug",
    'authDomain': "rohitfyp.firebaseapp.com",
    'projectId': "rohitfyp",
    'databaseURL': "https://rohitfyp-default-rtdb.firebaseio.com",
    'storageBucket': "rohitfyp.appspot.com",
    'messagingSenderId': "949237330189",
    'appId': "1:949237330189:web:7fbe16c501c95886900044",
    'measurementId': "G-MGQYKZFPYE"
}

# firebase authenticationn variable initialization 
firebase = pyrebase.initialize_app(firebaseConfig)
firebase_auth = firebase.auth()

# login method
def checkLogin():
    email = (lid.get())
    password = (lpass.get())
    try:
        user = firebase_auth.sign_in_with_email_and_password(email,password)
        tmsg.showinfo('Login', 'Login Success')
        Proceed_menu()
    except:
        tmsg.showinfo('Login', 'Incorrect Username or Password')


#Check for correct Path
def assure_path_exists(path):
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

#check for haarcascade file
def check_haarcascadefile():
    exists = os.path.isfile("haarcascade_frontalface_default.xml")
    if exists:
        pass
    else:
        tmsg._show(title='fechar file missing', message='some file is missing.Please contact me for help')
        window.destroy()

# capture face code
def TakeImages():
    check_haarcascadefile()
    columns = ['SERIAL NO.', '', 'ID', '', 'NAME', 'Email']
    assure_path_exists("StudentDetails/")
    assure_path_exists("TrainingImage/")
    serial = 0
    exists = os.path.isfile("StudentDetails\StudentDetails.csv")
    if exists:
        with open("StudentDetails\StudentDetails.csv", 'r') as csvFile1:
            reader1 = csv.reader(csvFile1)
            for l in reader1:
                serial = serial + 1
        serial = (serial // 2)
        csvFile1.close()
    else:
        with open("StudentDetails\StudentDetails.csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(columns)
            serial = 1
        csvFile1.close()
    Id = (senroll.get())
    name = (sname.get())
    
    cam = cv2.VideoCapture(0)
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    sampleNum = 0
    while (True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.05, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            sampleNum = sampleNum + 1
            cv2.imwrite("TrainingImage\ " + name + "." + str(serial) + "." + Id + '.' + str(sampleNum) + ".jpg",
                            gray[y:y + h, x:x + w])
            cv2.imshow('Taking Images', img)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
        elif sampleNum > 100:
            break
    cam.release()
    cv2.destroyAllWindows()
    res = "Images Taken for ID : " + Id
    row = [serial, '', Id, '', name, '', Id+'@heraldcollege.edu.np']
    with open('StudentDetails\StudentDetails.csv', 'a+') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    csvFile.close()

# method to extract image array and id 
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(imageNp)
        Ids.append(Id)
    return faces, Ids

# model defining method 
def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    faces, Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("TrainingImageLabel"+os.sep+"Trainner.yml")
    tmsg.showinfo('Train', 'Images Trainned')

# Face Recogniton method
def TrackImages():
    module_code = (modulecode.get())
    check_haarcascadefile()
    assure_path_exists("Attendance/")
    assure_path_exists("StudentDetails/")
    recognizer =cv2.face.LBPHFaceRecognizer_create() 
    exists3 = os.path.isfile("TrainingImageLabel\Trainner.yml")
    if exists3:
        recognizer.read("TrainingImageLabel\Trainner.yml")
    else:
        tmsg._show(title='Data Missing', message='Please click on Save Profile to reset data!!')
        return
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);

    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', '', 'Name', '', 'Date', '', 'Time', '', 'ModuleCode', '', 'Status']
    exists1 = os.path.isfile("StudentDetails\StudentDetails.csv")
    if exists1:
        df = pd.read_csv("StudentDetails\StudentDetails.csv")
    else:
        tmsg._show(title='Details Missing', message='Students details are missing, please check!')
        cam.release()
        cv2.destroyAllWindows()
        window.destroy()
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 2)
            serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
            if (conf < 50):
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa = df.loc[df['SERIAL NO.'] == serial]['NAME'].values
                ID = df.loc[df['SERIAL NO.'] == serial]['ID'].values
                ID = str(ID)
                ID = ID[1:-1]
                bb = str(aa)
                bb = bb[2:-2]
                mcode = module_code
                attendance = [str(ID), '', bb, '', str(date), '', str(timeStamp), '', mcode, '', 'P']

            else:
                Id = 'Unknown'
                bb = str(Id)
            cv2.putText(im, str(bb), (x, y + h), font, 1, (0, 251, 255), 2)
        cv2.imshow('Taking Attendance', im)
        if (cv2.waitKey(1) == ord('q')):
            break
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    exists = os.path.isfile("Attendance\Attendance_" + date + "_" + mcode + ".csv")
    if exists:
        with open("Attendance\Attendance_" + date + "_" + mcode + ".csv", 'a+') as csvFile1:
                writer = csv.writer(csvFile1)
                writer.writerow(attendance)
                csvFile1.close()
    else:
        with open("Attendance\Attendance_" + date + "_" + mcode + ".csv", 'a+') as csvFile1:
            writer = csv.writer(csvFile1)
            writer.writerow(col_names)
            writer.writerow(attendance)
        csvFile1.close()
    cam.release()
    cv2.destroyAllWindows()
    Testvalue = bb


#creating tkinter window
root = Tk()

# creating fixed geometry of the 
# tkinter window with dimensions 150x200 
root.geometry("150x200")
root.maxsize(580,550)
root.minsize(580,550)

#providing a title
root.title("Face Detection for Attendance")

image = Image.open("Background/appback2.png")
image=image.resize((580,600), Image.ANTIALIAS)
photo = ImageTk.PhotoImage(image)

# login frame 
l_login=Label(image=photo)
f_login=Frame(l_login,pady="25",padx="25")

lb0 =Label(f_login,text="Sign In",bg="#E6D294",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(columnspan=3,row=0,pady="15")
lb1 =Label(f_login,text="Email: ",font="lucida 10 bold").grid(column=0,row=2,pady="4")

lid =StringVar()
e1 =Entry(f_login,textvariable=lid,width="28").grid(column=1,row=2)
lb2 =Label(f_login,text="Password: ",font="lucida 10 bold").grid(column=0,row=3,pady="4")

lpass=StringVar()
e2=Entry(f_login,textvariable=lpass,width="28",show="*").grid(column=1,row=3)
btn=Button(f_login,text="login",bg="green",fg="white",width="10",font="lucida 10 bold",command=checkLogin)
btn.grid(columnspan=3,row=5,pady="10")

f_login.pack(pady="165")

l_login.pack(ipadx="100",fill=BOTH)

# student menu bar
def student(x):
    l2.pack_forget()
    l1.pack_forget()
    l.pack(ipadx="100",fill=BOTH)
    if(x==1):
        f3.pack(pady="115")
        f2.pack_forget()
        f21.pack_forget()
          

    if(x==2):
        f3.pack_forget()
        f21.pack_forget()
        f2.pack(pady="115")

# attendance menu bar
def attendance(y):
    l.pack_forget()
    l2.pack_forget()
    l1.pack(ipadx="150",fill=BOTH)
    if(y==1):
        fa.pack_forget()
        fd.pack(pady="120")
    if(y==2):
        fd.pack_forget()
        fa.pack(pady="135")
        
# more menu bar
def more(z):
    l.pack_forget()
    l1.pack_forget()
    l2.pack(ipadx="100",fill=BOTH)


# main page
def Proceed_menu():
    l_login.pack_forget()
    mainmenu = Menu(root)
    m1 = Menu(mainmenu, tearoff=0)
    m1.add_command(label="CaptureFace", command=lambda: student(1))
    m1.add_separator()
    m1.add_command(label="View Student Details", command=lambda: student(2))
    root.config(menu=mainmenu)
    mainmenu.add_cascade(label="Student", menu=m1)
    
    m2 = Menu(mainmenu, tearoff=0)
    m2.add_command(label="Detect", command=lambda:attendance(1))
    m2.add_separator()
    m2.add_command(label="View Attendance", command=lambda:attendance(2))
    root.config(menu=mainmenu)
    mainmenu.add_cascade(label="Attendance", menu=m2)
   

    m4 = Menu(mainmenu, tearoff=0)
    m4.add_command(label="Train",command=TrainImages)
    root.config(menu=mainmenu)
    mainmenu.add_cascade(label="Images", menu=m4)
    
    m3 = Menu(mainmenu, tearoff=0)
    m3.add_command(label="Help", command=lambda:more(1))
    m3.add_separator()
    m3.add_command(label="About Us", command=lambda:more(1))
    root.config(menu=mainmenu)
    mainmenu.add_cascade(label="More", menu=m3)



    
# capture face UI
l = Label(image=photo)
f3=Frame(l,pady="65",padx="25")
l0=Label(f3,text="Capture Face",bg="#E6D294",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(columnspan=3,row=0,pady="15")
l1=Label(f3,text="Full Name : ",font="lucida 10 bold").grid(column=0,row=1,pady="4")
sname=Entry(f3,width="28")
sname.grid(column=1,row=1)
l2=Label(f3,text="Enrollment No : ",font="lucida 10 bold").grid(column=0,row=2,pady="4")
senroll=Entry(f3,width="28")
senroll.grid(column=1,row=2)
btn=Button(f3,text="OK",bg="green",fg="white",width="10",font="lucida 10 bold",command=TakeImages)
btn.grid(columnspan=2,row=3,pady="20")
f3.pack(pady="50")


    
# view student details UI
global stu_id, stu_name, img,stu_email
stu_id , stu_name,img,stu_email= 0,0,"",0
def DisplayStudent():
    Found = 0
    filePath = "StudentDetails\StudentDetails.csv"
    sampleNum_detail = 1
    with open(filePath) as csvfile:
        reader = csv.DictReader(csvfile)
        student_id = (venroll.get())
        for row in reader:
            if (student_id == row['ID']):
                Found = 1
                break
        if(Found == 1):
            serial = row['SERIAL NO.']
            stu_id = student_id
            stu_name = row['NAME']
            stu_email = row['Email']
            if(("TrainingImage\ " + stu_name + "." + str(serial) + "." + stu_id + '.' + str(sampleNum_detail) + ".jpg")):
                img = Image.open("TrainingImage\ " + stu_name + "." + str(serial) + "." + stu_id + '.' + str(sampleNum_detail) + ".jpg")
                img = img.resize((100, 100), Image.ANTIALIAS)  
                img = ImageTk.PhotoImage(img)
        else:
            tmsg.showinfo('Error', 'Student Id not registered')         
    csvfile.close()
   
    l0=Label(f21,text="Student Details",bg="#E6D294",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(columnspan=3,row=0,pady="15")
    l3 = Label(f21,image=img)
    l3.image = img
    l3.grid(row=1)
    l1=Label(f21,text="Name : ",font="lucida 10 bold").grid(column=0,row=2,pady="4")
    l11=Label(f21,text=stu_name,width="28").grid(column=1,row=2)
    l2=Label(f21,text="Enrollment No : ",font="lucida 10 bold").grid(column=0,row=3,pady="4")
    l22=Label(f21,text=stu_id,width="28").grid(column=1,row=3)
    l3=Label(f21,text="Email : ",font="lucida 10 bold").grid(column=0,row=4,pady="4")
    l33=Label(f21,text=stu_email,width="28").grid(column=1,row=4)
    f21.pack(pady="100")
    f2.pack_forget()


# view student attendance report method
import os
import smtplib
from email.message import EmailMessage   
import matplotlib.pyplot as plt
import imghdr        
def Viewreport():
    import pandas as pd
    import glob 
    import tkinter as tk  
    from tkinter import simpledialog
    ROOT = tk.Tk()
    ROOT.withdraw()
    mocode = simpledialog.askstring(title="Module Code",
                                  prompt="Enter Module Code")  
    ROOT.destroy()
    student_id = str(venroll.get())
    print(student_id)
    count = 0
    Total = 12
    filecount = 0
    # print(type(student_id))
    files = glob.glob("Attendance\*.csv")
    for file in files:
        # print(filecount)
        with open(file) as filedata:
            df = pd.read_csv(file)
            Id = df['Id'].values
            moduleCode = df['ModuleCode'].values
            # print(type(Id))
            if(mocode==moduleCode[0]):
                filecount += 1
            for i in Id:
                    i = i[1:-1]
                    if(i == student_id and moduleCode[0] == mocode):
                        count += 1
                    else:
                        continue
    if(count>=1):
        # attendancepercent = int((count/Total)*100)
        # # print(attendancepercent)
        # tmsg.showinfo("Percentage",str(attendancepercent) + " %")
        p = count
        a = filecount-count
        attendance = [p,a]
        labels = ['present','absent']
        plt.pie(attendance,labels=labels,autopct = '%1.1f%%')
# plt.legend()
        plt.savefig("Graph\ "+student_id+'_'+mocode+'graph.png')
        plt.close()
        im = Image.open(r"Graph\ "+student_id+'_'+mocode+'graph.png') 
        im.show()
        if(filecount):
            Email_Address = os.environ.get('Email_User')
            Email_Password = os.environ.get('Email_Pass')

            msg = EmailMessage()
            msg['Subject'] = 'From Face Detection for Attendance'
            msg['From'] = Email_Address
            msg['To'] = str(student_id) + '@heraldcollege.edu.np'
            msg.set_content('Alert, Your attendance in module '+mocode)

            with open("Graph\ "+student_id+'_'+mocode+'graph.png','rb') as grp:
                file_data = grp.read()
                file_type = imghdr.what(grp.name)
                file_name = grp.name
            msg.add_attachment(file_data, maintype='image',subtype=file_type, filename=file_name)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(Email_Address,Email_Password)
                smtp.send_message(msg)
            grp.close()
            Proceed_menu()
    else:
        tmsg.showinfo("Error","Incorrect Id or Module Code")
            
def back():
    f21.pack_forget()
    f2.pack(pady="115")

# student details UI
f2=Frame(l,pady="90",padx="25")
l0=Label(f2,text="Student details",bg="#E6D294",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(columnspan=3,row=0,pady="10")
l2=Label(f2,text="Enrollment No : ",font="lucida 10 bold").grid(column=0,row=2,pady="4")
venroll=Entry(f2,width="28")
venroll.grid(column=1,row=2)
btn=Button(f2,text="Search",bg="green",fg="white",width="10",font="lucida 10 bold",command=DisplayStudent)
btn.grid(columnspan=3,row=7,pady="20")
btn1=Button(f2,text="View Report",bg="grey",fg="white",width="10",font="lucida 10 bold",command=Viewreport)
btn1.grid(columnspan=3,row=8,pady="10")
f2.pack(pady="115")

# student details display UI
f21=Frame(l,pady="30",padx="25")
l0=Label(f21,text="Student Details",bg="#E6D294",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(columnspan=3,row=0,pady="15")
l3 = Label(f21,image=img)
l3.image = img
l3.grid(row=1)
l1=Label(f21,text="Name : ",font="lucida 10 bold").grid(column=0,row=2,pady="4")
l11=Label(f21,text=stu_name,width="28").grid(column=1,row=2)
l2=Label(f21,text="Enrollment No : ",font="lucida 10 bold").grid(column=0,row=3,pady="4")
l22=Label(f21,text=stu_id,width="28").grid(column=1,row=3)
l3=Label(f21,text="Email : ",font="lucida 10 bold").grid(column=0,row=4,pady="4")
l33=Label(f21,text=stu_email,width="28").grid(column=1,row=4)
btn=Button(f21,text="Back",bg="green",fg="white",width="10",font="lucida 10 bold",command=back)
btn.grid(columnspan=1,row=5,pady="18")
f21.pack(pady="100")   


# Detect Face UI
l.pack(ipadx="100",fill=BOTH)
l1=Label(image=photo)
fd=Frame(l1,pady="90",padx="25")
ld=Label(fd,text="Welcome to Detect Section",bg="#E6D294",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(columnspan=3,row=0,pady="15")
ld1=Label(fd,text="Module Code : ",font="lucida 10 bold").grid(column=0,row=1,pady="4")
modulecode=Entry(fd,width="28")
modulecode.grid(column=1,row=1)
b1=Button(fd,text="Detect",bg="green",fg="white",width="10",font="lucida 10 bold",command=TrackImages)
b1.grid(columnspan=3,row=3,pady="20")

fd.pack(pady="120")

# view attendance method
def open_excel():
    import glob
    checkcount = 0
    files = glob.glob("Attendance\*.csv")
    v_modulecode = vmodulecode.get()
    v_date = vdate.get()
    attendancefile="Attendance\Attendance_"+ v_date +"_" + v_modulecode + ".csv"
    for file in files:
        if(file == attendancefile):
            checkcount = 1
    if(checkcount == 1):
        os.startfile(attendancefile)
    else:
        tmsg.showinfo("Not Found","Incorrect date format or module code")

# view attendance UI
fa=Frame(l1,pady="70",padx="10" ,height=150)
ld=Label(fa,text="View Attendance",bg="#E6D294",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(columnspan=3,row=0,pady="15",padx="10")
fa1=Label(fa,text="Module Code : ",font="lucida 10 bold").grid(column=0,row=1,pady="4")
vmodulecode=Entry(fa,width="28")
vmodulecode.grid(column=1,row=1)
fa2=Label(fa,text="Date (dd-mm-yyyy): ",font="lucida 10 bold").grid(column=0,row=2,pady="4")
vdate=Entry(fa,width="28")
vdate.grid(column=1,row=2)
btn=Button(fa,text="show",bg="green",fg="white",width="10",font="lucida 10 bold",command=open_excel)
btn.grid(columnspan=3,row=3,pady="0")

fa.pack(pady="135")
l1.pack(ipadx="150",fill=BOTH)



# more UI
l2=Label(image=photo)

f=Frame(l2,pady="25",padx="25")
lbl=Label(f,text="Help will be available in pro version",bg="orange",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(column=0,row=0)
lbl=Label(f,text="you can contact me for pro version",bg="orange",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(column=0,row=1)
lbl=Label(f,text="Email  :  rohitlama1999@gmail.com",bg="orange",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(column=0,row=2)
lbl=Label(f,text="mobile : 9819802885",bg="orange",fg="blue",font="lucida 10 bold",width="35",pady="4").grid(column=0,row=3)
f.pack(pady="195")

l2.pack(ipadx="100",fill=BOTH)

root.mainloop()
