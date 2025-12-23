from fastapi import FastAPI,Path,HTTPException,Query
from pydantic import BaseModel,Field,computed_field
from fastapi.responses import JSONResponse
from typing import Annotated,Literal,Optional
import json

app=FastAPI()

class patient(BaseModel):
    id:Annotated[str,Field(...,description="enter patient id",examples=['P001'])]
    name:Annotated[str,Field(...,description="Enter the patient name",examples=['umer'])]
    city:Annotated[str,Field(...,description='Enter the city name')]
    age:Annotated[int,Field(...,gt=0,lt=120)]
    gender:Annotated[Literal['male','female','other'],Field(description='Enter your gender')]
    height:Annotated[float,Field(...,gt=0,description="Enter the height greater then o and in meters")]
    weight:Annotated[float,Field(...,description='enter the weight in kg')]


    @computed_field
    @property
    def bmi(self)-> float:
        bmi=round(self.weight/(self.height**2),2)
        return bmi
    @ computed_field
    @property
    def virdect(self)-> str:
        if self.bmi < 18.5:
            return 'underweight'
        elif self.bmi <30:
            return 'Normal'
        else:
            return'obese'
class patient_update(BaseModel):

    name:Annotated[Optional[str],Field(default=None)]  
    city:Annotated[Optional[str],Field(default=None)] 
    age :Annotated[Optional[str],Field(default=None)]
    gender:Annotated[Optional[Literal['male','female']],Field(default=None)]  
    height:Annotated[Optional[float],Field(default=None,gt=0)]  
    weight:Annotated[Optional[float],Field(default=None,gt=0)] 

           



def load_data():
    with open('patients.json','r') as f:
        data=json.load(f)
    return data
def save_data(data):
    with open('patients.json ','w')as f:
        json.dump(data,f)



@app.get("/")
def halo():
    return{'msssage':'Patients managment system api .'}

@app.get("/about")
def about():
    return{'message':'FUlly functional patients managment system.'}

@app.get("/view")
def view():

    data=load_data()

    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id:str = Path(...,description='ID of the patient in the db ',example='P001')):
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=400,detail="Patient not found")

@app.get("/sort")

def sort_patient(sort_by:str= Query(...,description="Sort by on the base of height weight and bmi."),order:str=Query('asc',description='on the base of asc and desc')):
    valid_feild=['height','weight','bmi']


    if sort_by not in valid_feild:

        raise HTTPException(status_code=400,detail=f"Not valid feild select from{valid_feild}")
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail="select order by asc or desc")
    
    data=load_data()

    sorted_data=True if order=='desc'else False

    sorted_data=sorted(data.values(),key=lambda x:x.get(sort_by,0),reverse=sorted_data)

    return sorted_data

@app.post('/creat')
def creat_patient(patient:patient):
    # load data 
    data=load_data()

    # cheack that the patient id not already exest in data
    if patient.id in data:
        raise HTTPException(status_code=400,detail="patient id already exist")
    
    # add the new patient in dataset
    data[patient.id]=patient.model_dump(exclude=['id'])

    # save into json file
    save_data(data)

    return JSONResponse(status_code=201,content={'message':"patient sucessfully added"})

@app.put('/edit/{patient_id}')

def patient_update(patient_id:str,patient_update:patient_update):

#    load the data
    data=load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="patient not found .")
    
    #geting the past data of the patient in which user want to update.
    existing_patient_info=data[patient_id]

    update_patient_info=patient_update.model_dump(exclude_unset=True)

    for key,value in update_patient_info.items():
        existing_patient_info[key]=value

# convert the existing patient info into pydantic objec for the update of bmi and verdict.

    existing_patient_info['id']=patient_id
    patient_paydantic_object=patient(**existing_patient_info)

    # paydantic object into dict

    existing_patient_info=patient_paydantic_object.model_dump(exclude='id')



    #add this in to the data set
    data[patient_id]=existing_patient_info

    # save data
    data=save_data(data)
    return JSONResponse(status_code=200,content={'message':'patient updated sucessfully'})


@app.delete('/delete/{patient_id}')

def del_patient(patient_id:str):
    
    data= load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'patient delete sucessfully.'})












