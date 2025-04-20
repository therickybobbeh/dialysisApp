from datetime import datetime
from typing import Optional, List

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
from app.helpers.date_time import normalize_to_utc_day_bounds

HAPI_FHIR_BASE_URL = settings.HAPI_FHIR_BASE_URL
HAPI_FHIR_HEADERS={"Accept": "application/fhir+json", "Content-Type": "application/fhir+json"}
HAPI_FHIR_PATIENT_ID_BASE="KIDNEKT-PATIENT-ID-"
HAPI_FHIR_PROCEDURE_ID_BASE="KIDNEKT-PROCEDURE-ID-"


def _fhir_get_async_client():
    return httpx.AsyncClient(base_url=HAPI_FHIR_BASE_URL, headers=HAPI_FHIR_HEADERS)

def _fhir_get_sync_client():
    return httpx.Client(base_url=HAPI_FHIR_BASE_URL, headers=HAPI_FHIR_HEADERS)

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


def sync_fhir_create_patient_resource(patient_id, name, birth_date, gender, height):
    '''
    gender: "male" | "female" | "other" | "unknown"
    birth_date: datetime.date object or string formtted as yyyy-mm-dd
    name: <first name> <last name>
    '''
    with _fhir_get_sync_client() as hapi_client:
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
        response = hapi_client.put(
            f"Patient/{HAPI_FHIR_PATIENT_ID_BASE + str(patient_id)}",
            content=patient_rsc.model_dump_json()
        )
        response.raise_for_status()
        return response.json()


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



async def fhir_search_dialysis_sessions(
    patient_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date:   Optional[datetime] = None,
    limit:      int            = 1000
) -> List[dict]:
    async with _fhir_get_async_client() as hapi_client:
        # normalize your bounds once
        start_dt, end_dt = normalize_to_utc_day_bounds(start_date, end_date)

        # build a list of tuples so you can send both ge… and le… keys
        params = [
            ("_sort", "-date"),
            ("_count", str(limit)),
            ("_pretty", "true"),
        ]
        if patient_id is not None:
            params.append(("subject", f"Patient/{HAPI_FHIR_PATIENT_ID_BASE}{patient_id}"))
        if start_dt:
            params.append(("date", f"ge{start_dt.isoformat()}"))
        if end_dt:
            params.append(("date", f"le{end_dt.isoformat()}"))

        # no trailing '?' on the path
        response = await hapi_client.get("Procedure", params=params)
        response.raise_for_status()

        bundle_rsc = Bundle(**response.json())
        sessions = []
        for entry in (bundle_rsc.entry or []):
            sessions.append(_fhir_parse_dialysis_session_resource(entry.resource))
        return sessions


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
    """
    Parse a Procedure resource's dialysis-session extension into a dict,
    converting quantities and strings safely.
    """
    # Find the root extension
    ext_root = None
    for ext in getattr(procedure_rsc, 'extension', []) or []:
        if ext.url == 'dialysis-session':
            ext_root = ext
            break
    if not ext_root:
        return {}
    data = {}
    for sub in ext_root.extension:
        key = sub.url
        if hasattr(sub, 'valueString') and sub.valueString is not None:
            data[key] = sub.valueString
        else:
            qty = getattr(sub, 'valueQuantity', None)
            val = getattr(qty, 'value', None) if qty else None
            data[key] = float(val) if val is not None else None
    # Extract IDs
    raw_sub = getattr(procedure_rsc.subject, 'reference', '')
    raw_id = getattr(procedure_rsc, 'id', '')
    try:
        pid = int(raw_sub.split(f"Patient/{HAPI_FHIR_PATIENT_ID_BASE}")[-1])
    except:
        pid = None
    try:
        sid = int(raw_id.split(HAPI_FHIR_PROCEDURE_ID_BASE)[-1])
    except:
        sid = None

    # Extract session_date
    session_date = getattr(procedure_rsc, 'performedDateTime', None)

    # Return the parsed data
    return {
        'patient_id': pid,
        'session_id': sid,
        'id': sid,  # Map session_id to id
        'session_date': session_date,
        **data
    }



######################################################################################################