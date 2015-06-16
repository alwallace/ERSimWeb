import sqlite3
from flask import g
from flask.ext.login import current_user
from ersim import query_db, commit_db, lastid_db
from ersim import app

code_actions = ('start compressions', 'stop compressions', 'set compressions depth', 'set compressions rate',
				'start ventilations', 'stop ventilations', 'set ventilations volume', 'set ventilations rate', 'set compression to ventilation ratio', 
				'add iv access', 'add io access', 'add advanced airway', 
				'give cardioversion',
				'give epinephrine', 'set epinephrine dose', 'set epinephrine route', 'set epinephrine rate',
				'give amiodarone', 'set amiodarone dose', 'set amiodarone route', 'set amiodarone rate',
				'check PETCO2', 'check diastolic pressure', 'check pulse', 'check blood pressure', 'check rhythm', 'check hypovolemia', 'check hypoxia', 'check acidosis', 'check potassium', 'check hypothermia', 'check tension pneumothorax', 'check tamponade', 'check toxins', 'check pulmonary thrombosis', 'check coronary thrombosis', 'check waveform capnography'
				)

def setCompressions(patientCodeState, cDepth, cRate):
	patientCodeState.ccDepth = cDepth
	patientCodeState.ccRate = cRate
	patientCodeState.saveCurrentState()

def setVentilations(patientCodeState, vVolume, vRate, cToVRatio):
	patientCodeState.vVolume = vVolume
	patientCodeState.vRate = vRate
	patientCodeState.cToVRatio = cToVRatio
	saveCurrentState(patientCodeState)

def addAdvancedAirway(patientCodeState, airwayType):
	patientCodeState.airwayType = airwayType
	saveCurrentState(patientCodeState)

def addIVAccess(patientCodeState):
	patientCodeState.ivAccess += '18g;'
	saveCurrentState(patientCodeState)

def addIVAccess(patientCodeState):
	patientCodeState.ioAccess += 'IO port;'
	saveCurrentState(patientCodeState)

def giveCardioversion(patientCodeState):
	patientCodeState.cardiovesion = 'True'
	saveCurrentState(patientCodeState)
	patientCodeState.cardiovesion = 'False'
	saveCurrentState(patientCodeState)

def giveDefibrillation(patientCodeState):
	patientCodeState.defibrillation = 'True'
	saveCurrentState(patientCodeState)
	patientCodeState.defibrillation = 'False'
	saveCurrentState(patientCodeState)

def giveEpinephrine(patientCodeState, epiDose, epiRoute, epiRate):
	patientCodeState.epiDose = epiDose
	patientCodeState.epiRoute = epiRoute
	patientCodeState.epiRate = epiRate
	saveCurrentState(patientCodeState)
	patientCodeState.epiDose = '0'
	patientCodeState.epiRoute = ''
	patientCodeState.epiRate = '0'
	saveCurrentState(patientCodeState)

def giveAmiodarone(patientCodeState, amioDose, amioRoute, amioRate):
	patientCodeState.amioDose = amioDose
	patientCodeState.amioRoute = amioRoute
	patientCodeState.amioRate = amioRate
	saveCurrentState(patientCodeState)
	patientCodeState.amioDose = '0'
	patientCodeState.amioRoute = ''
	patientCodeState.amioRate = '0'
	saveCurrentState(patientCodeState)

def checkPETCO(patientCodeState):
	return


def saveCurrentState(patientCodeState):
		commit_db("INSERT INTO patient_state (patient_id, previous_state_id, timestamp, heart_rate, blood_pressure, pulse, heart_rhythm, chest_compression_depth, chest_compression_rate, airway_type, ventilation_rate, ventilation_volume, compression_ventilation_ratio, iv_access, io_access, cardioversion, defibrillation, epinephrine_dose, amiodarone_dose, epinephrine_route, amiodarone_route, epinephrine_rate, amiodarone_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,)", (patientCodeState.patientID, patientCodeState.previousState.patientStateID, 'CURRENT_TIMESTAMP', patientCodeState.heartRate, patientCodeState.bloodPressure, patientCodeState.pulse, patientCodeState.heartRhythm, patientCodeState.ccDepth, patientCodeState.ccRate, patientCodeState.airwayType, patientCodeState.vRate, patientCodeState.vVolume, patientCodeState.cToVRatio, patientCodeState.ivAccess, patientCodeState.ioAccess, patientCodeState.epiDose, patientCodeState.amioDose, patientCodeState.epiRoute, patientCodeState.amioRoute, patientCodeState.epiRate, patientCodeState.amioRate,))
		patientCodeState.patientStateID = lastid_db()

class PatientCodeState:
	def __init__(self, patientID):
		self.patientStateID = -1
		self.patientID = patientID
		self.previousStateID = -1
		self.timestamp = '-1'
		self.heartRate = '0'
		self.bloodPressure = '0/0'
		self.pulse = '0'
		self.heartRhythm = 'Ventricular Fibrillation'
		self.ccDepth = '0'
		self.ccRate = '0'
		self.airwayType = 'natural'
		self.vRate = '0'
		self.vVolume = '0'
		self.cToVRatio = '0:0'
		self.ivAccess = ''
		self.ioAccess = ''
		self.cardioversion = 'False'
		self.defibrillation = 'False'
		self.epiDose = '0'
		self.amioDose = '0'
		self.epiRoute = ''
		self.amioRoute = ''
		self.epiRate = '0'
		self.amioRate = '0'

