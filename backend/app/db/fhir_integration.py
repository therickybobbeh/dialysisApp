import httpx
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.procedure import Procedure
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.quantity import Quantity
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.humanname import HumanName
from app.core.config import settings

HAPI_FHIR_BASE_URL = settings.HAPI_FHIR_BASE_URL
HAPI_FHIR_HEADERS={"Accept": "application/fhir+json", "Content-Type": "application/fhir+json"}
HAPI_FHIR_PATIENT_ID_BASE="KIDNEKT-PATIENT-ID-"
HAPI_FHIR_PROCEDURE_ID_BASE="KIDNEKT-PROCEDURE-ID-"


def _fhir_get_async_client():
    return httpx.AsyncClient(base_url=HAPI_FHIR_BASE_URL, headers=HAPI_FHIR_HEADERS)


def _fhir_create_patient_resource_ext(height):
    return Extension(
        url="height",
        valueQuantity=Quantity(
            value=height,
            unit="in",
            system="http://unitsofmeasure.org",
            code="in"
        )
    )


async def fhir_create_patient_resource(patient_id, name, birth_date, gender, height):
    '''
    gender: "male" | "female" | "other" | "unknown"
    birth_date: datetime.date object or string formtted as yyyy-mm-dd
    name: <first name> <last name>
    '''
    async with _fhir_get_async_client() as hapi_client:
        given_name, family_name = name.split(" ")
        patient_rsc = Patient(
            id=HAPI_FHIR_PATIENT_ID_BASE + str(patient_id),
            name=[HumanName(
                given=[given_name],
                family=family_name
            )],
            active=True,
            gender=gender,
            birthDate=str(birth_date),
            extension=[_fhir_create_patient_resource_ext(height)]
        )
        response = await hapi_client.put(
            f"Patient/{HAPI_FHIR_PATIENT_ID_BASE + str(patient_id)}",
            content=patient_rsc.model_dump_json()
        )
        response.raise_for_status()
        return response.json()


async def fhir_get_patient_resource(patient_id):
    '''
    patient_id: patient's id as given by kidnekt backend, NOT the hapi fhir version. Must be prefixed by HAPI_FHIR_PATIENT_ID_BASE TO AVOID ERRORS
    '''
    async with _fhir_get_async_client() as hapi_client:
        response = await hapi_client.get(
            f"Patient/{HAPI_FHIR_PATIENT_ID_BASE + str(patient_id)}"
        )
        response.raise_for_status()
        patient_rsc = Patient(**response.json())
        obj = {
            "id": int(patient_rsc.id[len(HAPI_FHIR_PATIENT_ID_BASE):]),
            "name": f"{patient_rsc.name[0].given[0]} {patient_rsc.name[0].family}",
            "height": float(patient_rsc.extension[0].valueQuantity.value)
        }
        return obj


async def fhir_search_dialysis_sessions(patient_id=None, start_date=None, end_date=None, limit=1000):
    async with _fhir_get_async_client() as hapi_client:
        search_params = {
            "_sort": "-date",
            "_count": limit,
            "_pretty": True
        }
        if patient_id is not None:
            search_params["subject"] = f"Patient/{HAPI_FHIR_PATIENT_ID_BASE + str(patient_id)}"
        if start_date is not None:
            search_params["date"] = f"ge{str(start_date)}"
        if end_date is not None:
            search_params["date"] = f"le{str(end_date)}"
        response = await hapi_client.get(
            "Procedure?",
            params=search_params
        )
        response.raise_for_status()
        bundle_rsc = Bundle(**response.json())
        dialysis_sessions = []
        for entry in bundle_rsc.entry:
            dialysis_sessions.append(_fhir_parse_dialysis_session_resource(entry.resource))
        return dialysis_sessions


async def fhir_delete_dialysis_session_resource(session_id):
    async with _fhir_get_async_client() as hapi_client:
        response = await hapi_client.delete(
            f"Procedure/{HAPI_FHIR_PROCEDURE_ID_BASE + str(session_id)}"
        )
        response.raise_for_status()
        return response.json()


def _fhir_create_dialysis_session_resource_ext(session_type, weight, diastolic, systolic, effluent_volume, duration, protein):
    # TODO: store all info here as Observations

    return Extension(
        url="dialysis-session",
        extension=[
            Extension(
                url="session_type",
                valueString=session_type,
            ),
            Extension(
                url="weight",
                valueQuantity=Quantity(
                    value=weight,
                    unit="kg",
                    system="http://unitsofmeasure.org",
                    code="kg"
                )
            ),
            Extension(
                url="diastolic",
                valueQuantity=Quantity(
                    value=diastolic,
                    unit="mmHg",
                    system="http://unitsofmeasure.org",
                    code="mm[Hg]"
                )
            ),
            Extension(
                url="systolic",
                valueQuantity=Quantity(
                    value=systolic,
                    unit="mmHg",
                    system="http://unitsofmeasure.org",
                    code="mm[Hg]"
                )
            ),
            Extension(
                url="effluent_volume",
                valueQuantity=Quantity(
                    value=effluent_volume,
                    unit="mL",
                    system="http://unitsofmeasure.org",
                    code="mL"
                )
            ),
            Extension(
                url="duration",
                valueQuantity=Quantity(
                    value=duration,
                    unit="min",
                    system="http://unitsofmeasure.org",
                    code="min"
                )
            ),
            Extension(
                url="protein",
                valueQuantity=Quantity(
                    value=protein,
                    unit="g/L",
                    system="http://unitsofmeasure.org",
                    code="g/L"
                )
            )
        ]
    )


async def fhir_create_dialysis_session_resource(session_id, patient_id, date, session_type, weight, diastolic, systolic, effluent_volume, duration, protein):
    async with _fhir_get_async_client() as hapi_client:
        procedure_rsc = Procedure(
            id=HAPI_FHIR_PROCEDURE_ID_BASE + str(session_id),
            status="completed",
            code=CodeableConcept(
                coding=[
                    Coding(
                        system="http://snomed.info/sct",
                        code="108241001",
                        display="CCPD"
                    )
                ]
            ),
            subject=Reference(reference=f"Patient/{HAPI_FHIR_PATIENT_ID_BASE + str(patient_id)}"),
            performedDateTime=f"{date}T00:00:00Z",
            extension=[_fhir_create_dialysis_session_resource_ext(
                session_type=session_type,
                weight=weight,
                diastolic=diastolic,
                systolic=systolic,
                effluent_volume=effluent_volume,
                duration=duration,
                protein=protein
            )]
        )

        response = await hapi_client.put(
            f"Procedure/{HAPI_FHIR_PROCEDURE_ID_BASE + str(session_id)}",
            content=procedure_rsc.model_dump_json()
        )
        response.raise_for_status()
        return response.json()


async def fhir_get_dialysis_session_resource(session_id):
    async with _fhir_get_async_client() as hapi_client:
        response = await hapi_client.get(
            f"Procedure/{HAPI_FHIR_PROCEDURE_ID_BASE + str(session_id)}"
        )
        response.raise_for_status()
        procedure_rsc = Procedure(**response.json())
        return _fhir_parse_dialysis_session_resource(procedure_rsc)


def _fhir_parse_dialysis_session_resource(procedure_rsc):
    dialysis_session_ext = procedure_rsc.extension[0]
    dialysis_session_ext_obj = {}
    for entry in dialysis_session_ext.extension:
        if entry.url == "session_type":
            dialysis_session_ext_obj[entry.url] = entry.valueString
        else:
            dialysis_session_ext_obj[entry.url] = float(entry.valueQuantity.value)
    obj = {
        "patient_id": procedure_rsc.subject.reference[len(f"Patient/{HAPI_FHIR_PATIENT_ID_BASE}"):],
        "session_id": procedure_rsc.id[len(HAPI_FHIR_PROCEDURE_ID_BASE):], 
        **dialysis_session_ext_obj
    }
    return obj


######################################################################################################