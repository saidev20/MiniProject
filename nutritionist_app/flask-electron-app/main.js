const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let flaskApp;

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
    }
  });

  // Load the Flask app (localhost).
  mainWindow.loadURL('http://127.0.0.1:5000/');

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  // Start the Flask app
  flaskApp = spawn('python', ['app.py']); // Replace with your actual Flask script name
  
  flaskApp.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`);
  });

  flaskApp.stderr.on('data', (data) => {
    console.error(`Flask Error: ${data}`);
  });

  flaskApp.on('close', (code) => {
    console.log(`Flask app exited with code ${code}`);
  });

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
