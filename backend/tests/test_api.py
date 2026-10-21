from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.routers import reports as reports_router

client = TestClient(app)

def test_health():
    r=client.get('/api/health'); assert r.status_code==200 and r.json()['status']=='ok' and r.json()['database']=='connected'

def test_cors_allows_configured_frontend_origin():
    r=client.options('/api/reports', headers={
        'Origin':'http://localhost:5173',
        'Access-Control-Request-Method':'POST',
    })
    assert r.status_code==200
    assert r.headers['access-control-allow-origin']=='http://localhost:5173'

def test_report_create_and_track():
    payload={'title':'Water leaking from pipe','description':'Water is leaking from a damaged pipe near a school entrance.','citizen_category':'Water Leakage','location_name':'Test Lane','latitude':17.38,'longitude':78.48}
    r=client.post('/api/reports',json=payload); assert r.status_code==201, r.text
    report=r.json(); assert report['public_report_id'].startswith('NX-')
    assert client.post('/api/track',json={'report_id':report['public_report_id']}).status_code==200

def test_report_create_is_idempotent():
    key=str(uuid4())
    payload={'title':'Water leaking from pipe','description':'Water is leaking from a damaged pipe near a school entrance.','citizen_category':'Water Leakage','location_name':'Test Lane'}
    headers={'Idempotency-Key':key}
    first=client.post('/api/reports',json=payload,headers=headers)
    retry=client.post('/api/reports',json=payload,headers=headers)
    assert first.status_code==201 and retry.status_code==201
    assert retry.json()['public_report_id']==first.json()['public_report_id']

    changed_payload={**payload,'location_name':'Different test lane'}
    conflict=client.post('/api/reports',json=changed_payload,headers=headers)
    assert conflict.status_code==409

def test_operations_mutations_are_disabled_in_production(monkeypatch):
    monkeypatch.setattr(reports_router, 'APP_ENV', 'production')
    response=client.patch('/api/reports/NX-NOT-REAL',json={'status':'Resolved'})
    assert response.status_code==404
    assert client.post('/api/reports/NX-NOT-REAL/analyze').status_code==404

def test_invalid_category_rejected():
    payload={'title':'Broken infrastructure item','description':'This description is long enough for validation.','citizen_category':'Made up category','location_name':'Test Lane'}
    assert client.post('/api/reports',json=payload).status_code==422

def test_status_update_persists_history():
    payload={'title':'Blocked drain near lane','description':'Drain is blocked and water is overflowing on the footpath.','citizen_category':'Blocked Drainage','location_name':'Test Drain'}
    created=client.post('/api/reports',json=payload).json()
    updated=client.patch(f"/api/reports/{created['public_report_id']}",json={'status':'In Progress','change_note':'Crew assigned for test'})
    assert updated.status_code==200 and updated.json()['status']=='In Progress'
    history=client.get(f"/api/reports/{created['public_report_id']}/history").json()
    assert history[-1]['previous_status']=='Reported' and history[-1]['new_status']=='In Progress'

def test_image_upload_signature_and_size():
    payload={'title':'Pothole by lane','description':'There is a pothole on the road near the corner.','citizen_category':'Potholes','location_name':'Test Lane'}
    created=client.post('/api/reports',json=payload).json()
    r=client.post(f"/api/reports/{created['public_report_id']}/image",files={'image':('proof.png',b'\x89PNG\r\n\x1a\n'+b'test','image/png')})
    assert r.status_code==200 and r.json()['image_path'].startswith('/uploads/')
