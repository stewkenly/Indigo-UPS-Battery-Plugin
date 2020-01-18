#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2011, Benjamin Schollnick. All rights reserved.
# http://www.schollnick.net/Wordpress

################################################################################
# Python imports
import exceptions
import os
import sys
import time

################################################################################
# Globals
################################################################################

plugin_id 	= "com.schollnick.indigoplugin.BatteryMonitor"
plugin_name = "BatteryMonitor"
plugin_manual = ""

current_device_version = 4


################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		"""
		Initialization of Battery Monitor
		"""
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = pluginPrefs.get("showDebugInfo", False)
		#
		#	Perform a version check on the Find My iDevices plugin itself
		#
#		self.VersionCheck ()
		self.monitors = []
		self.verify_preference ( "Timing", 5)
		self.verify_preference ( "PowerFailureTiming", 1)
		self.verify_preference ( "SupressLogging", True)

	########################################
	def __del__(self):
		indigo.PluginBase.__del__(self)

	########################################
	# Built-in control methods
	########################################
	def startup(self):
		"""
		Startup and initialization code
		"""
		#
		#	Load settings from Indigo Database
		#
		self.debug = self.pluginPrefs.get("showDebugInfo", False)
		self.debugLog ( "Debug Mode is On (Only recommended for Testing Purposes)")



	########################################
	def shutdown(self):
		# Nothing to do since deviceStopComm will be called for each of our
		# devices and that's how we'll clean up
		pass

	def manualDeviceUpdate (self, action):
	#
	#	Update requested via Trigger Action
	#
		pass

	def manualDeviceUpdate_menutrigger (self):
	#
	#	Update requested via Menu item
	#
		pass

	########################################
	def	verify_preference ( self, preferencekey, default_value):
		if self.pluginPrefs.has_key ( preferencekey):
			return
		else:
			self.pluginPrefs [ preferencekey ] = default_value


	def	verify_device_properties ( self, dev, propertyname, boolean = False, default_value = "") :
		newProps = dev.pluginProps			#dev.globalProps[plugin_id]
		if newProps.has_key (propertyname):
			return
		else:
			if boolean:
				newProps[propertyname] = True
			else:
				newProps[propertyname] = default_value

			dev.replacePluginPropsOnServer(newProps)

	def	update_device_property ( self, dev, propertyname, new_value = ""):
		newProps = dev.pluginProps
		newProps.update ( {propertyname : new_value} )
		dev.replacePluginPropsOnServer(newProps)
		return None

	########################################

	def	deviceStartComm (self, dev):
	#
	#
	#
		self.verify_device_properties (dev, "device_version", boolean = False, default_value = "000")
		self.verify_device_properties (dev, "Model", boolean = False, default_value = "")
		self.verify_device_properties (dev, "ACPower", boolean = True )
		self.verify_device_properties (dev, "PowerSource", boolean = False, default_value = "" )

		dv = int(dev.pluginProps["device_version"])
		if current_device_version <> dv:
			dev.stateListOrDisplayStateIdChanged()
			self.update_device_property ( dev, "device_version", new_value = current_device_version )
#			indigo.server.log ("\tUpdated Device States")

#		indigo.server.log ("Processing Device - %s" % dev.name)

		if dev.deviceTypeId == "BatteryMonitor":
			self.monitors.append ( dev.id )
			if len(self.monitors) >= 2:
				self.errorLog ("Only One Battery & UPS Monitor can be used.")
				self.monitors = self.monitors [0]

	def	deviceStopComm (self, dev):
#		indigo.server.log ("Removing %s" % dev.name)
		if dev.deviceTypeId == "BatteryMonitor":
			self.monitors.remove ( dev.id )

	def	get_battery_status ( self ):
		import subprocess
		proc = subprocess.Popen ( ['pmset', '-g', 'batt'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

		out, err = proc.communicate ()
		out = out.split ("\n")

		if len(out) == 2:
			return ("AC Power - No Battery", "No Battery or UPS", False, 0, 0, 0,0 )

		power_status = out[0].split ("'")[1]
		data = out[1].split ("\t")
		ups_model = data[0]
		data = data[1].split (";")
		percentage = data[0][0:-1]#data[1][0:percent_locale]
		charging = data[1].find("discharging") == -1
		if not charging:
			time	= data[2][0:data[2].find(":")+3].strip()
			hours	= data[2][0:time.find(":")+1]
			min		= data[2][time.find(":")+2:time.find(":")+4]
		else:
			time = 0
			hours  = 0
			min  = 0

		return (power_status, ups_model, charging, percentage, time, hours, min)

	def runConcurrentThread(self):
		try:
			while self.stopThread == False:
				power_status, ups_model, charging, percentage, timestring, hours, min = self.get_battery_status ()
				if self.pluginPrefs["SupressLogging"] == True and charging:
					pass
				else:
					indigo.server.log ("\tPower Status    - %s" % power_status)
					indigo.server.log ("\tUPS Model       - %s" % ups_model)
					indigo.server.log ("\tCharging Status - %s" % charging)
					indigo.server.log ("\tBattery Charge  - %02s" % percentage )
					if charging == True:
						indigo.server.log ("Refreshing in %s Minutes" % self.pluginPrefs["Timing"])
					else:
						indigo.server.log ("Refreshing in %s Minutes" % self.pluginPrefs["PowerFailureTiming"])


				if self.monitors == {}:
					indigo.server.log ("\tNo Battery & UPS Monitor device defined.")
				else:
					if len(self.monitors) >= 1:
						BatteryMonitor = indigo.devices[ self.monitors[0] ]
						if BatteryMonitor.states["Model"] <> ups_model:
							BatteryMonitor.updateStateOnServer ( "Model", ups_model)

						if BatteryMonitor.states["ACPower"] <> power_status:
							BatteryMonitor.updateStateOnServer ( "ACPower", power_status)

						if BatteryMonitor.states["Charging"] <> charging:
							BatteryMonitor.updateStateOnServer ( "Charging", charging)

						if BatteryMonitor.states["BatteryLevel"] <> percentage:
							BatteryMonitor.updateStateOnServer ( "BatteryLevel", percentage)

						if BatteryMonitor.states["BatteryTimeRemaining"] <> int(hours)*60 + int(min):
							BatteryMonitor.updateStateOnServer ( "BatteryTimeRemaining", int(hours)*60 + int(min) )

						if BatteryMonitor.states["PowerSource"] <> power_status:
							BatteryMonitor.updateStateOnServer ( "PowerSource", power_status)

						BatteryMonitor.updateStateOnServer ( "TimeDateStamp", time.ctime ( ) )

				if charging == True:
					self.sleep ( int(self.pluginPrefs["Timing"]) * 60 )
				else:
					self.sleep ( int(self.pluginPrefs["PowerFailureTiming"]) * 60 )

		except self.StopThread:
			self.stopThread = True
			self.autopoll_activated = False
			indigo.server.log ("Stopping Plugin")


