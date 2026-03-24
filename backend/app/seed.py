from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Aeronave, Aeropuerto, TipoIncidente, Usuario
from .security import get_password_hash


ARGENTINA_AIRPORTS = [
    {"codigo_iata": "AEP", "codigo_icao": "SABE", "nombre": "Aeroparque Jorge Newbery", "ciudad": "Buenos Aires", "provincia": "CABA", "categoria": "Internacional"},
    {"codigo_iata": "EZE", "codigo_icao": "SAEZ", "nombre": "Ministro Pistarini", "ciudad": "Ezeiza", "provincia": "Buenos Aires", "categoria": "Internacional"},
    {"codigo_iata": "COR", "codigo_icao": "SACO", "nombre": "Ingeniero Aeronautico Ambrosio L. V. Taravella", "ciudad": "Cordoba", "provincia": "Cordoba", "categoria": "Internacional"},
    {"codigo_iata": "BRC", "codigo_icao": "SAZS", "nombre": "Teniente Luis Candelaria", "ciudad": "San Carlos de Bariloche", "provincia": "Rio Negro", "categoria": "Internacional"},
    {"codigo_iata": "CRD", "codigo_icao": "SAVC", "nombre": "General Enrique Mosconi", "ciudad": "Comodoro Rivadavia", "provincia": "Chubut", "categoria": "Internacional"},
    {"codigo_iata": "EQS", "codigo_icao": "SAVE", "nombre": "Esquel", "ciudad": "Esquel", "provincia": "Chubut", "categoria": "Nacional"},
    {"codigo_iata": "FMA", "codigo_icao": "SARF", "nombre": "Formosa", "ciudad": "Formosa", "provincia": "Formosa", "categoria": "Internacional"},
    {"codigo_iata": "GPO", "codigo_icao": "SAZG", "nombre": "General Pico", "ciudad": "General Pico", "provincia": "La Pampa", "categoria": "Nacional"},
    {"codigo_iata": "IGR", "codigo_icao": "SARI", "nombre": "Cataratas del Iguazu", "ciudad": "Puerto Iguazu", "provincia": "Misiones", "categoria": "Internacional"},
    {"codigo_iata": "IRJ", "codigo_icao": "SANL", "nombre": "Capitan Vicente Almandos Almonacid", "ciudad": "La Rioja", "provincia": "La Rioja", "categoria": "Nacional"},
    {"codigo_iata": "MDZ", "codigo_icao": "SAME", "nombre": "El Plumerillo", "ciudad": "Mendoza", "provincia": "Mendoza", "categoria": "Internacional"},
    {"codigo_iata": "PSS", "codigo_icao": "SARP", "nombre": "Libertador General Jose de San Martin", "ciudad": "Posadas", "provincia": "Misiones", "categoria": "Internacional"},
    {"codigo_iata": "RGL", "codigo_icao": "SAWG", "nombre": "Piloto Civil Norberto Fernandez", "ciudad": "Rio Gallegos", "provincia": "Santa Cruz", "categoria": "Internacional"},
    {"codigo_iata": "RGA", "codigo_icao": "SAWE", "nombre": "Hermes Quijada", "ciudad": "Rio Grande", "provincia": "Tierra del Fuego", "categoria": "Internacional"},
    {"codigo_iata": "FDO", "codigo_icao": "SADF", "nombre": "San Fernando", "ciudad": "San Fernando", "provincia": "Buenos Aires", "categoria": "Nacional"},
    {"codigo_iata": "LUQ", "codigo_icao": "SAOU", "nombre": "Brigadier Mayor Cesar Raul Ojeda", "ciudad": "San Luis", "provincia": "San Luis", "categoria": "Nacional"},
    {"codigo_iata": "AFA", "codigo_icao": "SAMR", "nombre": "San Rafael", "ciudad": "San Rafael", "provincia": "Mendoza", "categoria": "Nacional"},
    {"codigo_iata": "SDE", "codigo_icao": "SANE", "nombre": "Vicecomodoro Angel de la Paz Aragones", "ciudad": "Santiago del Estero", "provincia": "Santiago del Estero", "categoria": "Nacional"},
    {"codigo_iata": "RSA", "codigo_icao": "SAZR", "nombre": "Santa Rosa", "ciudad": "Santa Rosa", "provincia": "La Pampa", "categoria": "Nacional"},
    {"codigo_iata": "VDM", "codigo_icao": "SAVV", "nombre": "Gobernador Castello", "ciudad": "Viedma", "provincia": "Rio Negro", "categoria": "Nacional"},
    {"codigo_iata": "VME", "codigo_icao": "SAOR", "nombre": "Villa Reynolds", "ciudad": "Villa Mercedes", "provincia": "San Luis", "categoria": "Nacional"},
    {"codigo_iata": "SLA", "codigo_icao": "SASA", "nombre": "Martin Miguel de Guemes", "ciudad": "Salta", "provincia": "Salta", "categoria": "Internacional"},
    {"codigo_iata": "TUC", "codigo_icao": "SANT", "nombre": "Teniente Benjamin Matienzo", "ciudad": "Tucuman", "provincia": "Tucuman", "categoria": "Internacional"},
    {"codigo_iata": "CTC", "codigo_icao": "SANC", "nombre": "Coronel Felipe Varela", "ciudad": "Catamarca", "provincia": "Catamarca", "categoria": "Nacional"},
    {"codigo_iata": "PRA", "codigo_icao": "SAAP", "nombre": "General Justo Jose de Urquiza", "ciudad": "Parana", "provincia": "Entre Rios", "categoria": "Nacional"},
    {"codigo_iata": "RCU", "codigo_icao": "SAOC", "nombre": "Area de Material Rio Cuarto", "ciudad": "Rio Cuarto", "provincia": "Cordoba", "categoria": "Nacional"},
    {"codigo_iata": "RES", "codigo_icao": "SARE", "nombre": "Resistencia", "ciudad": "Resistencia", "provincia": "Chaco", "categoria": "Internacional"},
    {"codigo_iata": "JUJ", "codigo_icao": "SASJ", "nombre": "Gobernador Horacio Guzman", "ciudad": "San Salvador de Jujuy", "provincia": "Jujuy", "categoria": "Internacional"},
    {"codigo_iata": "UAQ", "codigo_icao": "SANU", "nombre": "Domingo Faustino Sarmiento", "ciudad": "San Juan", "provincia": "San Juan", "categoria": "Nacional"},
    {"codigo_iata": "LGS", "codigo_icao": "SAMM", "nombre": "Comodoro Ricardo Salomon", "ciudad": "Malargue", "provincia": "Mendoza", "categoria": "Nacional"},
    {"codigo_iata": "PMY", "codigo_icao": "SAVY", "nombre": "El Tehuelche", "ciudad": "Puerto Madryn", "provincia": "Chubut", "categoria": "Nacional"},
    {"codigo_iata": "RCQ", "codigo_icao": "SATR", "nombre": "Reconquista", "ciudad": "Reconquista", "provincia": "Santa Fe", "categoria": "Nacional"},
    {"codigo_iata": "MDQ", "codigo_icao": "SAZM", "nombre": "Astor Piazzolla", "ciudad": "Mar del Plata", "provincia": "Buenos Aires", "categoria": "Internacional"},
    {"codigo_iata": "NQN", "codigo_icao": "SAZN", "nombre": "Presidente Peron", "ciudad": "Neuquen", "provincia": "Neuquen", "categoria": "Internacional"},
    {"codigo_iata": "BHI", "codigo_icao": "SAZB", "nombre": "Comandante Espora", "ciudad": "Bahia Blanca", "provincia": "Buenos Aires", "categoria": "Internacional"},
    {"codigo_iata": "REL", "codigo_icao": "SAVT", "nombre": "Almirante Marco Andres Zar", "ciudad": "Trelew", "provincia": "Chubut", "categoria": "Internacional"},
    {"codigo_iata": "ROS", "codigo_icao": "SAAR", "nombre": "Rosario Islas Malvinas", "ciudad": "Rosario", "provincia": "Santa Fe", "categoria": "Internacional"},
    {"codigo_iata": "USH", "codigo_icao": "SAWH", "nombre": "Malvinas Argentinas", "ciudad": "Ushuaia", "provincia": "Tierra del Fuego", "categoria": "Internacional"},
    {"codigo_iata": "SFN", "codigo_icao": "SAAV", "nombre": "Sauce Viejo", "ciudad": "Santa Fe", "provincia": "Santa Fe", "categoria": "Nacional"},
    {"codigo_iata": "CNQ", "codigo_icao": "SARC", "nombre": "Doctor Fernando Piragine Niveyro", "ciudad": "Corrientes", "provincia": "Corrientes", "categoria": "Internacional"},
    {"codigo_iata": "VLG", "codigo_icao": "SAZV", "nombre": "Villa Gesell", "ciudad": "Villa Gesell", "provincia": "Buenos Aires", "categoria": "Nacional"},
    {"codigo_iata": "CPC", "codigo_icao": "SAZY", "nombre": "Aviador Carlos Campos", "ciudad": "San Martin de los Andes", "provincia": "Neuquen", "categoria": "Nacional"},
    {"codigo_iata": "CUT", "codigo_icao": "SAZW", "nombre": "Cutral-Co", "ciudad": "Cutral-Co", "provincia": "Neuquen", "categoria": "Nacional"},
    {"codigo_iata": "TTG", "codigo_icao": "SAST", "nombre": "General Enrique Mosconi", "ciudad": "Tartagal", "provincia": "Salta", "categoria": "Nacional"},
    {"codigo_iata": "COC", "codigo_icao": "SAAC", "nombre": "Comodoro Pierrestegui", "ciudad": "Concordia", "provincia": "Entre Rios", "categoria": "Nacional"},
    {"codigo_iata": None, "codigo_icao": "SADD", "nombre": "Don Torcuato", "ciudad": "Don Torcuato", "provincia": "Buenos Aires", "categoria": "Nacional"},
    {"codigo_iata": "GNR", "codigo_icao": "SAHR", "nombre": "Doctor Arturo Umberto Illia", "ciudad": "General Roca", "provincia": "Rio Negro", "categoria": "Nacional"},
    {"codigo_iata": "TDL", "codigo_icao": "SAZT", "nombre": "Heroes de Malvinas", "ciudad": "Tandil", "provincia": "Buenos Aires", "categoria": "Nacional"},
    {"codigo_iata": "FTE", "codigo_icao": "SAWC", "nombre": "Comandante Armando Tola", "ciudad": "El Calafate", "provincia": "Santa Cruz", "categoria": "Internacional"},
    {"codigo_iata": "SST", "codigo_icao": "SAZL", "nombre": "Santa Teresita", "ciudad": "Santa Teresita", "provincia": "Buenos Aires", "categoria": "Nacional"},
    {"codigo_iata": "NEC", "codigo_icao": "SAZO", "nombre": "Necochea", "ciudad": "Necochea", "provincia": "Buenos Aires", "categoria": "Nacional"},
    {"codigo_iata": "AOL", "codigo_icao": "SARL", "nombre": "Paso de los Libres", "ciudad": "Paso de los Libres", "provincia": "Corrientes", "categoria": "Nacional"},
    {"codigo_iata": "LPG", "codigo_icao": "SADL", "nombre": "La Plata", "ciudad": "La Plata", "provincia": "Buenos Aires", "categoria": "Nacional"},
    {"codigo_iata": "JNI", "codigo_icao": "SAAJ", "nombre": "Junin", "ciudad": "Junin", "provincia": "Buenos Aires", "categoria": "Nacional"},
    {"codigo_iata": None, "codigo_icao": "SAOL", "nombre": "Laboulaye", "ciudad": "Laboulaye", "provincia": "Cordoba", "categoria": "Nacional"},
    {"codigo_iata": "LCM", "codigo_icao": "SACC", "nombre": "La Cumbre", "ciudad": "La Cumbre", "provincia": "Cordoba", "categoria": "Nacional"},
    {"codigo_iata": None, "codigo_icao": "SA7B", "nombre": "Huinca Renanco", "ciudad": "Huinca Renanco", "provincia": "Cordoba", "categoria": "Nacional"},
]


ARGENTINA_AIRCRAFT = [
    {"matricula": "LV-FPS", "modelo": "B737-800", "fabricante": "Boeing", "operador": "Aerolineas Argentinas", "tipo_aeronave": "Comercial", "peso_maximo_despegue": 79015},
    {"matricula": "LV-KHQ", "modelo": "A320", "fabricante": "Airbus", "operador": "Jetsmart", "tipo_aeronave": "Comercial", "peso_maximo_despegue": 77000},
    {"matricula": "LV-GKO", "modelo": "EMB-190", "fabricante": "Embraer", "operador": "Austral", "tipo_aeronave": "Comercial", "peso_maximo_despegue": 51800},
    {"matricula": "LV-KEF", "modelo": "B737-8 MAX", "fabricante": "Boeing", "operador": "Aerolineas Argentinas", "tipo_aeronave": "Comercial", "peso_maximo_despegue": 82190},
    {"matricula": "LV-HFR", "modelo": "A320neo", "fabricante": "Airbus", "operador": "Flybondi", "tipo_aeronave": "Comercial", "peso_maximo_despegue": 79000},
    {"matricula": "LV-CHQ", "modelo": "Saab 340B", "fabricante": "Saab", "operador": "LADE", "tipo_aeronave": "Regional", "peso_maximo_despegue": 13155},
    {"matricula": "LV-GAQ", "modelo": "B737-700", "fabricante": "Boeing", "operador": "Aerolineas Argentinas", "tipo_aeronave": "Comercial", "peso_maximo_despegue": 70080},
    {"matricula": "LV-BYE", "modelo": "Learjet 60", "fabricante": "Bombardier", "operador": "Ejecutiva", "tipo_aeronave": "Ejecutiva", "peso_maximo_despegue": 10659},
    {"matricula": "LV-FUR", "modelo": "Cessna 172S", "fabricante": "Cessna", "operador": "Escuela de Vuelo", "tipo_aeronave": "Instruccion", "peso_maximo_despegue": 1157},
    {"matricula": "LV-CBM", "modelo": "PA-34 Seneca", "fabricante": "Piper", "operador": "Aviacion General", "tipo_aeronave": "Aviacion General", "peso_maximo_despegue": 2155},
    {"matricula": "LV-FQN", "modelo": "Cessna 208B Grand Caravan", "fabricante": "Cessna", "operador": "Carga Regional", "tipo_aeronave": "Carga", "peso_maximo_despegue": 3969},
    {"matricula": "LV-HUM", "modelo": "Bell 412", "fabricante": "Bell", "operador": "Helicopteros Argentina", "tipo_aeronave": "Helicoptero", "peso_maximo_despegue": 5398},
    {"matricula": "LV-VCN", "modelo": "Robinson R44", "fabricante": "Robinson", "operador": "Helicopteros Argentina", "tipo_aeronave": "Helicoptero", "peso_maximo_despegue": 1134},
    {"matricula": "LV-X497", "modelo": "IA-63 Pampa III", "fabricante": "FAdeA", "operador": "Fuerza Aerea Argentina", "tipo_aeronave": "Militar", "peso_maximo_despegue": 5000},
    {"matricula": "TC-66", "modelo": "C-130H Hercules", "fabricante": "Lockheed Martin", "operador": "Fuerza Aerea Argentina", "tipo_aeronave": "Militar", "peso_maximo_despegue": 70305},
    {"matricula": "LV-CNT", "modelo": "B1900D", "fabricante": "Beechcraft", "operador": "Regional", "tipo_aeronave": "Regional", "peso_maximo_despegue": 7764},
    {"matricula": "LV-ABD", "modelo": "ATR 72-600", "fabricante": "ATR", "operador": "Regional", "tipo_aeronave": "Regional", "peso_maximo_despegue": 23000},
    {"matricula": "LV-FSK", "modelo": "A321-200", "fabricante": "Airbus", "operador": "Charter", "tipo_aeronave": "Comercial", "peso_maximo_despegue": 93500},
    {"matricula": "LV-MZA", "modelo": "DHC-6 Twin Otter", "fabricante": "De Havilland Canada", "operador": "Patagonia", "tipo_aeronave": "STOL", "peso_maximo_despegue": 5670},
    {"matricula": "LV-PTN", "modelo": "PA-25 Pawnee", "fabricante": "Piper", "operador": "Trabajo Aereo", "tipo_aeronave": "Agricola", "peso_maximo_despegue": 1315},
]


def _sync_airports(db: Session) -> None:
    existing_by_icao = {airport.codigo_icao: airport for airport in db.scalars(select(Aeropuerto)).all()}

    for payload in ARGENTINA_AIRPORTS:
        airport = existing_by_icao.get(payload["codigo_icao"])
        if airport:
            airport.codigo_iata = payload["codigo_iata"]
            airport.nombre = payload["nombre"]
            airport.ciudad = payload["ciudad"]
            airport.provincia = payload["provincia"]
            airport.categoria = payload["categoria"]
            airport.estado = "Activo"
            continue

        db.add(Aeropuerto(**payload))


def _sync_aircraft(db: Session) -> None:
    existing_by_registration = {aircraft.matricula: aircraft for aircraft in db.scalars(select(Aeronave)).all()}

    for payload in ARGENTINA_AIRCRAFT:
        aircraft = existing_by_registration.get(payload["matricula"])
        if aircraft:
            aircraft.modelo = payload["modelo"]
            aircraft.fabricante = payload["fabricante"]
            aircraft.operador = payload["operador"]
            aircraft.tipo_aeronave = payload["tipo_aeronave"]
            aircraft.peso_maximo_despegue = payload["peso_maximo_despegue"]
            continue

        db.add(Aeronave(**payload))


def seed_initial_data(db: Session) -> None:
    if not db.scalar(select(Usuario.id).limit(1)):
        db.add(
            Usuario(
                nombre="Administrador Demo",
                email="admin@aspredictive.local",
                password_hash=get_password_hash("Admin12345"),
                rol="administrador",
                estado=True,
            )
        )

    _sync_airports(db)

    _sync_aircraft(db)

    if not db.scalar(select(TipoIncidente.id).limit(1)):
        db.add_all(
            [
                TipoIncidente(codigo_oaci="REIN", nombre="Reingreso Pista", categoria="Pista"),
                TipoIncidente(codigo_oaci="BIRD", nombre="Colision con Fauna", categoria="Fauna"),
                TipoIncidente(codigo_oaci="ENGINE", nombre="Falla de Motor", categoria="Tecnico"),
                TipoIncidente(codigo_oaci="RUNWAY", nombre="Incursion de Pista", categoria="Pista"),
            ]
        )

    db.commit()
