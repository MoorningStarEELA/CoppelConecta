const admin = require("firebase-admin");
const serviceAccount = require("../coppelconecta-firebase-adminsdk-4x1g0-5f3a2b8e7d.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://coppelconecta.firebaseio.com",
});

const db = admin.firestore();

module.exports = db;
