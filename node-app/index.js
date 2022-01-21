const express = require('express')
const app = express()
const port = 5983
const awaitRequest = require('./await-request');

const bodyParser = require('body-parser');

const VERIFICATION_TOKEN = "Q7PG2W_NQyOgwTrIDEs7Lw";
const zoomMeetingId = 85138039085


app.post('/zoomEndpoint', bodyParser.raw({ type: 'application/json' }), async (req, res) => {
    function Response(statusCode, msg) {
        console.log(statusCode, msg);
        return res.status(statusCode).send(msg);
    }
    Response(200, 'Participant Joined')
    let eventObj;
    try {
        eventObj = JSON.parse(req.body);
    } catch (err) {
        console.log(err);
    }
    if (req.headers.authorization === VERIFICATION_TOKEN) {
        const meetingID = eventObj.payload.object.id;
        
        if (eventObj.event === 'meeting.participant_joined') {
            let participant = eventObj.payload.object.participant;
            let participantJoinDetails = {
                meetingID: meetingID,
                name: participant.user_name,
                joinTime: participant.join_time,
                userID: participant.user_id,
                email: participant.email
            };
            if (meetingID === zoomMeetingId) {
                const options = {
                    method: 'POST',
                    url: `http://localhost:5982/updateAttendance`,
                    body: {
                        email: participant.email,
                    },
                    json: true
                };
                await awaitRequest(options);
                console.log(participantJoinDetails);
            }
           
        }
    }

})
app.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`)
})