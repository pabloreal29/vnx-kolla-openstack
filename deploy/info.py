from pymongo import MongoClient
client = MongoClient("10.1.2.83",27017) #Aquí hay que poner la IP de bbdd en Net2
db = client.school
estudiante = db.students.find_one()
numero_docs = db.students.count_documents({})

print("Trabajo Final de CNVR - Grupo 1")
print(f"Base de datos obtenida de la asignatura BDFI. Contiene datos de {numero_docs} estudiantes")
print("A continuación se muestran los datos de un estudiante a modo de ejemplo")

print(f"Nombre: {estudiante['name']}")
print(f"Edad: {estudiante['age']}")
print(f"Nacionalidad: {estudiante['nationality']}")
print(f"Email: {estudiante['email']}")
