# MenuTitle: HT LetterSpacer Manager
# -*- coding: utf-8 -*-

__doc__ = """
Manage LetterSpacer settings.
"""

import uuid
from vanilla import *


class LetterSpacerManager:
	def __init__(self):
		self.font = Font

		if self.font is None:
			Message("Select a font project!", "No font selected")
		# return

		# Make a list of all categories of the glyphs in the font
		self.categories = []
		for glyph in self.font.glyphs:
			if glyph.category and glyph.category not in self.categories:
				self.categories.append(glyph.category)

		self.sub_categories = ["Any"]
		for glyph in self.font.glyphs:
			if glyph.subCategory and glyph.subCategory not in self.sub_categories:
				self.sub_categories.append(glyph.subCategory)

		# dictionary of all font settings with key: category
		# for every category, dictionary with keys: subcategory, case, value, reference glyph, filter
		if self.font.userData["com.eweracs.HTLSManager.fontSettings"]:
			self.font_settings = dict(self.font.userData["com.eweracs.HTLSManager.fontSettings"])
		else:
			self.font_settings = {}

		# if the category is not in the dictionary, add it
		for category in self.categories:
			if category not in self.font_settings:
				self.font_settings[category] = {}

		# make a vanilla window with two tabs: font settings and master settings
		self.w = FloatingWindow((584, 1), "HT LetterSpacer Manager")

		self.metrics = {
			"margin": 10
		}

		self.w.tabs = Tabs("auto", ["Font settings", "Master settings", "Visualiser"])

		self.fontSettingsTab = self.w.tabs[0]
		self.masterSettingsTab = self.w.tabs[1]
		self.visualiserTab = self.w.tabs[2]

		#########################
		#                       #
		#   Font settings tab   #
		#                       #
		#########################

		self.fontSettingsTab.title = TextBox("auto", "Font settings")

		self.font_settings_groups = {}

		self.font_settings_elements = set()

		# add one vanilla group per category in self.categories

		# then add a vanilla group to self.w for each category
		for category in self.categories:
			category_group = Group("auto")
			category_group.title = TextBox("auto", category)
			# add a button to add a new setting for the category
			category_group.addButton = Button("auto", "Add rule", callback=self.add_font_setting)

			stack_views = []

			# for every setting in font_settings: add a group to the category group, using the key from the setting to
			# find the group
			# the group contains a title, a dropdown for the subcategory, a dropdown for the case, an editable text field
			# for the value, a textfield for the reference glyph, a textfield for the filter
			# the group has a button to remove the settin

			for setting in self.font_settings[category]:
				stack_views.append(dict(view=self.add_setting_group(category, setting)))

			category_group.stackView = VerticalStackView("auto",
			                                             views=stack_views,
			                                             spacing=10,
			                                             edgeInsets=(10, 10, 10, 10))

			group_rules = [
				"H:|-margin-[title]-margin-|",
				"H:|[stackView]|",
				"H:|-20-[addButton]",
				"V:|[title][stackView][addButton]-margin-|"

			]

			category_group.addAutoPosSizeRules(group_rules, self.metrics)

			setattr(self.fontSettingsTab, category, category_group)

		font_tab_rules = [
			"H:|-margin-[title]-margin-|",
		]

		# for each category group, add a rule to the font_tab_rules list
		for category in self.categories:
			font_tab_rules.append("H:|-margin-[%s]-margin-|" % category)
		# make a vertical rule combining all category groups
		font_tab_rules.append("V:|-margin-[title]-margin-[%s]-margin-|" % "]-margin-[".join(self.categories))

		self.fontSettingsTab.addAutoPosSizeRules(font_tab_rules, self.metrics)

		#########################
		#                       #
		#  Master settings tab  #
		#                       #
		#########################

		self.masterSettingsTab.title = TextBox("auto", "Master settings")

		for category in self.categories:
			category_group = Group("auto")
			category_group.title = TextBox("auto", category)

			# for every setting in font_settings: add a group to the category group, using the key from the setting to
			# find the group
			# the group contains a title and a text field for every entry in the setting

			for setting in self.font_settings[category]:
				# if the setting is empty, skip it
				if len(self.font_settings[category][setting]) == 0:
					continue
				current_setting = self.font_settings[category][setting]
				setting_group = Group("auto")
				setting_group.subcategory = TextBox("auto", current_setting["subcategory"])
				setting_group.case = TextBox("auto", current_setting["case"])
				setting_group.value = EditText("auto", text=current_setting["value"])
				setting_group.referenceGlyph = TextBox("auto", current_setting["referenceGlyph"])
				setting_group.filter = TextBox("auto", current_setting["filter"])

				group_rules = [
					"H:|-margin-[subcategory]-margin-[case]-margin-[value(60)]-margin-[referenceGlyph(==value)]-margin-"
					"[filter(==value)]-margin-|",
					"V:|[subcategory]|",
					"V:|[case]|",
					"V:|[value]|",
					"V:|[referenceGlyph]|",
					"V:|[filter]|"
				]

				setting_group.addAutoPosSizeRules(group_rules, self.metrics)
				setattr(category_group, "setting" + str(setting), setting_group)

			group_rules = [
				"H:|-margin-[title]-margin-|",
			]

			vertical_rule = "V:|[title]"

			# for every setting in the font settings for the category, add a rule to the group_rules
			try:
				if self.font_settings[category]:
					for setting in self.font_settings[category]:
						group_rules.append("H:|-margin-[%s]-margin-|" % ("setting" + str(setting)))
						# add the setting to the vertical rule
						vertical_rule += "-margin-[%s]" % ("setting" + str(setting))

			except KeyError:
				pass

			vertical_rule += "-margin-|"

			group_rules.append(vertical_rule)

			category_group.addAutoPosSizeRules(group_rules, self.metrics)

			setattr(self.masterSettingsTab, category, category_group)

		master_tab_rules = [
			"H:|-margin-[title]-margin-|",
		]

		# for each category group, add a rule to the font_tab_rules list
		for category in self.categories:
			master_tab_rules.append("H:|-margin-[%s]-margin-|" % category)
		# make a vertical rule combining all category groups
		master_tab_rules.append("V:|-margin-[title]-margin-[%s]-margin-|" % "]-margin-[".join(self.categories))

		self.masterSettingsTab.addAutoPosSizeRules(master_tab_rules, self.metrics)

		rules = [
			"H:|-margin-[tabs]-margin-|",
			"V:|-margin-[tabs]-margin-|",
		]

		self.w.addAutoPosSizeRules(rules, self.metrics)

		self.w.addAutoPosSizeRules(rules, self.metrics)
		self.w.open()
		self.w.makeKey()

	def add_setting_group(self, category, setting):
		# if the setting is empty, skip it
		if len(self.font_settings[category][setting]) == 0:
			return False
		current_setting = self.font_settings[category][setting]
		setting_group = Group("auto")
		setting_group.subcategory = PopUpButton("auto", self.sub_categories, callback=self.update_font_setting)
		setting_group.case = PopUpButton("auto", ["Any", "upper", "lower"], callback=self.update_font_setting)
		setting_group.value = EditText("auto",
		                               continuous=False,
		                               text=current_setting["value"],
		                               callback=self.update_font_setting)
		setting_group.referenceGlyph = ComboBox("auto",
		                                        [glyph.name for glyph in self.font.glyphs],
		                                        callback=self.update_font_setting)
		setting_group.filter = EditText("auto",
		                                continuous=False,
		                                placeholder="None",
		                                text=current_setting["filter"],
		                                callback=self.update_font_setting)
		setting_group.removeButton = Button("auto", "Remove rule",
		                                    callback=self.remove_font_setting)

		setting_group.subcategory.set(current_setting["subcategory"])
		setting_group.case.set(current_setting["case"])
		setting_group.referenceGlyph.set(current_setting["referenceGlyph"])

		group_rules = [
			"H:|-margin-[subcategory]-margin-[case]-margin-[value(60)]-margin-[referenceGlyph(==value)]-margin-"
			"[filter(==value)]-margin-[removeButton]",
			"V:|[subcategory]|",
			"V:|[case]|",
			"V:|[value]|",
			"V:|[referenceGlyph]|",
			"V:|[filter]|",
			"V:|[removeButton]|"
		]

		setting_group.addAutoPosSizeRules(group_rules, self.metrics)

		# add all group elements to the elements set
		self.font_settings_elements.add(setting_group.subcategory)
		self.font_settings_elements.add(setting_group.case)
		self.font_settings_elements.add(setting_group.value)
		self.font_settings_elements.add(setting_group.referenceGlyph)
		self.font_settings_elements.add(setting_group.filter)
		self.font_settings_elements.add(setting_group.removeButton)

		# add the group to the setting group dictionary with ID
		self.font_settings_groups[setting] = setting_group

		return setting_group

	def add_font_setting(self, sender):
		setting_id = str(uuid.uuid4()).replace("-", "")
		try:
			for category in self.categories:
				if getattr(self.fontSettingsTab, category).addButton == sender:
					self.font_settings[category][setting_id] = {
						"subcategory": 0,
						"case": 0,
						"value": 1,
						"referenceGlyph": "",
						"filter": ""
					}
					break

		except Exception as e:
			print(e)

		# find the stack view for the category
		for category in self.categories:
			if getattr(self.fontSettingsTab, category).addButton == sender:
				getattr(self.fontSettingsTab, category).stackView.appendView(self.add_setting_group(category, setting_id))
				break

		self.w.resize(584, 1)

		self.write_font_settings()

	def remove_font_setting(self, sender):
		# remove the view that the remove button belongs to from the stack view
		try:
			for category in self.categories:
				for setting in self.font_settings[category]:
					if self.font_settings_groups[setting].removeButton == sender:
						getattr(self.fontSettingsTab, category).stackView.removeView(self.font_settings_groups[setting])
						del self.font_settings[category][setting]
		except Exception as e:
			print(e)

		self.w.resize(584, 1)

		self.write_font_settings()

	def update_font_setting(self, sender):
		try:
			for category in self.categories:
				for setting in self.font_settings[category]:
					for key in self.font_settings[category][setting]:
						if getattr(
								getattr(
									getattr(self.fontSettingsTab, category), "setting" + str(setting)
								), key
						) == sender:
							self.font_settings[category][setting][key] = sender.get()
							break

		except Exception as e:
			print(e)

		self.write_font_settings()

	def write_font_settings(self):
		self.font.userData["com.eweracs.HTLSManager.fontSettings"] = self.font_settings


LetterSpacerManager()
