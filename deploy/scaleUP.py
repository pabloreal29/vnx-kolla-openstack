import requests

# Obtener la URL de escalamiento hacia arriba
scale_up_url = "http://10.0.0.250:8000/v1/signal/arn%3Aopenstack%3Aheat%3A%3A59084731532a4314a773f83946cc215b%3Astacks/example/56894308-d2f7-4850-9932-ddd9421dd697/resources/instance_scaledown_policy?SignatureMethod=HmacSHA256&SignatureVersion=2&AWSAccessKeyId=be8f6f10edc640d1bd2e36c3e52f5a0f&Signature=gI%2FmuWqschBDFu3XxZImEG37%2Bc%2ByIWoy6Sdpy6s65Bs%3D"

# Realizar la solicitud HTTP POST
response = requests.post(scale_up_url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    print("Operación de escalamiento hacia arriba exitosa")
else:
    print("Hubo un error al intentar escalar hacia arriba")
    print(response.status_code)
