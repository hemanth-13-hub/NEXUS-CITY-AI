from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r=client.get('/api/health'); assert r.status_code==200 and r.json()['status']=='ok'

def test_report_create_and_track():
    payload={'title':'Water leaking from pipe','description':'Water is leaking from a damaged pipe near a school entrance.','citizen_category':'Water Leakage','location_name':'Test Lane','latitude':17.38,'longitude':78.48}
    r=client.post('/api/reports',json=payload); assert r.status_code==201, r.text
    report=r.json(); assert report['public_report_id'].startswith('NX-')
    assert client.post('/api/track',json={'report_id':report['public_report_id']}).status_code==200

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
