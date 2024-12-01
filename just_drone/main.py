from fastapi import FastAPI, Request

import math
import rospy
from clover import srv
from std_srvs.srv import Trigger

rospy.init_node('flight')

get_telemetry = rospy.ServiceProxy('get_telemetry', srv.GetTelemetry)
navigate = rospy.ServiceProxy('navigate', srv.Navigate)
navigate_global = rospy.ServiceProxy('navigate_global', srv.NavigateGlobal)
set_position = rospy.ServiceProxy('set_position', srv.SetPosition)
set_velocity = rospy.ServiceProxy('set_velocity', srv.SetVelocity)
set_attitude = rospy.ServiceProxy('set_attitude', srv.SetAttitude)
set_rates = rospy.ServiceProxy('set_rates', srv.SetRates)
land = rospy.ServiceProxy('land', Trigger)


def goto(x=0, y=0, z=0, yaw=float('nan'), speed=0.5, frame_id='aruco_map', auto_arm=False, tolerance=0.2):
    navigate(x=x, y=y, z=z, yaw=yaw, speed=speed, frame_id=frame_id, auto_arm=auto_arm)

    while not rospy.is_shutdown():
        telem = get_telemetry(frame_id='navigate_target')
        if math.sqrt(telem.x ** 2 + telem.y ** 2 + telem.z ** 2) < tolerance:
            break
        rospy.sleep(0.2)


app = FastAPI()

@app.post('/alice')
async def handle_alice_command(request: Request):
    data = await request.json()

    command = data['request']['command'].lower()
    message_id = data['session']['message_id']

    if message_id == 0:
        response_text = 'Дрон готов'
    else: 
        response_text = 'Команда не распознана'


    if 'взлет' in command:
        response_text = 'Дрон взлетает'
        navigate(z=1, auto_arm=True, frame_id='body')
    
    if 'перемещение' in command:
        x, y, z = 0, 0, 0
        if 'вперед' in command:
            x += 1
        elif 'назад' in command:
            x -= 1
        if 'влево' in command:
            y += 1
        elif 'вправо' in command:
            y -= 1
        if 'вверх' in command:
            z += 1
        elif 'вниз' in command:
            z -= 1
        navigate(x=x, y=y, z=z, frame_id='body')
        response_text = 'Дрон перемешяется'

    if 'посадка' in command:
        response_text = 'Дрон садится'
        land()
    
    return {
        'response': {
            'text': response_text,
            'end_session': False
        },
        'version': '1.0'
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)