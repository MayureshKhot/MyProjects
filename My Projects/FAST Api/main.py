from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import model, schemas, database

model.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Employee Management API")

#Dependency for DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close() # Close the connection once operation is performed
        
#Create employee
@app.post("/employees/", response_model=schemas.EmployeeBase)
def create_employee(employee: schemas.EmployeeCreate, db: Session=Depends(get_db)):
    db_emp = db.query(model.Employee).filter(model.Employee.email==employee.email).first()
    if db_emp:
        raise HTTPException(status_code=400, detail = "Email already registered")
    
    new_employee = model.Employee(dict.employee)
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@app.get("/emploees/", response_model = list[schemas.EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    return db.query(model.Employee).all()

@app.get("/employees/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee=db.query(model.Employee).filter(model.Employee.id==employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.put("/employees/{employee_id}", response_model = schemas.EmployeeResponse)
def update_employee(employee_id: int, emp_data: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.query(model.Employee).filter(model.Employee.id==employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    for key, value in emp_data.dict.items():
        setattr(employee, key, value)
        
    db.commit()
    db.refresh(employee)
    return employee

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session=Depends(get_db)):
    employee = db.query(model.Employee).filter(model.Employee.id==employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db.delete(employee)
    db.commit()
    return {"message": f"Employee {employee_id} deleted successfully"}