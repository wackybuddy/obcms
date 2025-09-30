# OBC Management System - Component Library

## Table of Contents
- [Overview](#overview)
- [Buttons](#buttons)
- [Forms](#forms)
- [Cards](#cards)
- [Navigation](#navigation)
- [Alerts & Messages](#alerts--messages)
- [Tables](#tables)
- [Modals](#modals)
- [Status Indicators](#status-indicators)
- [Layout Components](#layout-components)

## Overview

This component library provides ready-to-use UI components for the OBC Management System. All components follow the established design system and are fully responsive and accessible.

### Usage Instructions
1. Copy the HTML code for the component you need
2. Ensure your template extends the base template or includes the necessary CSS
3. Customize classes and content as needed
4. Test across different screen sizes

## Buttons

### Primary Button
```html
<button class="bg-bangsamoro-gradient text-white px-6 py-3 rounded-lg font-semibold 
               hover:transform hover:translate-y-[-2px] hover:shadow-lg 
               transition-all duration-300 focus:outline-none focus:ring-2 
               focus:ring-blue-500 focus:ring-offset-2">
    <i class="fas fa-save mr-2"></i>
    Primary Action
</button>
```

### Secondary Button
```html
<button class="bg-gradient-to-r from-pink-400 to-purple-500 text-white px-6 py-3 
               rounded-lg font-semibold hover:from-pink-500 hover:to-purple-600 
               transition-all duration-300 focus:outline-none focus:ring-2 
               focus:ring-pink-500 focus:ring-offset-2">
    <i class="fas fa-edit mr-2"></i>
    Secondary Action
</button>
```

### Outline Button
```html
<button class="border-2 border-blue-600 text-blue-600 px-6 py-3 rounded-lg 
               font-semibold hover:bg-blue-600 hover:text-white 
               transition-all duration-300 focus:outline-none focus:ring-2 
               focus:ring-blue-500 focus:ring-offset-2">
    <i class="fas fa-cancel mr-2"></i>
    Cancel
</button>
```

### Icon-Only Button
```html
<button class="bg-gray-100 hover:bg-gray-200 p-3 rounded-lg 
               transition-colors duration-200 focus:outline-none focus:ring-2 
               focus:ring-gray-400 focus:ring-offset-2">
    <i class="fas fa-search text-gray-600"></i>
</button>
```

### Button Group
```html
<div class="flex space-x-2">
    <button class="bg-blue-600 text-white px-4 py-2 rounded-l-lg 
                   hover:bg-blue-700 transition-colors duration-200">
        <i class="fas fa-list mr-2"></i>
        List View
    </button>
    <button class="bg-gray-200 text-gray-700 px-4 py-2 
                   hover:bg-gray-300 transition-colors duration-200">
        <i class="fas fa-th-large mr-2"></i>
        Grid View
    </button>
    <button class="bg-gray-200 text-gray-700 px-4 py-2 rounded-r-lg 
                   hover:bg-gray-300 transition-colors duration-200">
        <i class="fas fa-map mr-2"></i>
        Map View
    </button>
</div>
```

## Forms

### Basic Input Field
```html
<div class="mb-4">
    <label for="community-name" class="block text-sm font-medium text-gray-700 mb-2">
        Community Name <span class="text-red-500">*</span>
    </label>
    <input type="text" 
           id="community-name" 
           name="community_name"
           class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg 
                  focus:border-blue-500 focus:ring focus:ring-blue-200 
                  focus:ring-opacity-50 transition-all duration-200"
           placeholder="Enter community name"
           required>
    <p class="mt-1 text-sm text-gray-500">Enter the official name of the community</p>
</div>
```

### Select Dropdown
```html
<div class="mb-4">
    <label for="region" class="block text-sm font-medium text-gray-700 mb-2">
        Region
    </label>
    <select id="region" 
            name="region"
            class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg 
                   focus:border-blue-500 focus:ring focus:ring-blue-200 
                   focus:ring-opacity-50 transition-all duration-200 bg-white">
        <option value="">Select a region</option>
        <option value="region-ix">Region IX (Zamboanga Peninsula)</option>
        <option value="region-xii">Region XII (SOCCSKSARGEN)</option>
    </select>
</div>
```

### Textarea
```html
<div class="mb-4">
    <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
        Description
    </label>
    <textarea id="description" 
              name="description" 
              rows="4"
              class="w-full px-4 py-3 border-2 border-gray-300 rounded-lg 
                     focus:border-blue-500 focus:ring focus:ring-blue-200 
                     focus:ring-opacity-50 transition-all duration-200 resize-vertical"
              placeholder="Enter detailed description..."></textarea>
</div>
```

### Checkbox Group
```html
<div class="mb-4">
    <fieldset>
        <legend class="block text-sm font-medium text-gray-700 mb-3">
            Available Services
        </legend>
        <div class="space-y-2">
            <label class="flex items-center">
                <input type="checkbox" 
                       name="services[]" 
                       value="education"
                       class="h-4 w-4 text-blue-600 border-gray-300 rounded 
                              focus:ring-blue-500">
                <span class="ml-2 text-sm text-gray-700">Education</span>
            </label>
            <label class="flex items-center">
                <input type="checkbox" 
                       name="services[]" 
                       value="healthcare"
                       class="h-4 w-4 text-blue-600 border-gray-300 rounded 
                              focus:ring-blue-500">
                <span class="ml-2 text-sm text-gray-700">Healthcare</span>
            </label>
            <label class="flex items-center">
                <input type="checkbox" 
                       name="services[]" 
                       value="infrastructure"
                       class="h-4 w-4 text-blue-600 border-gray-300 rounded 
                              focus:ring-blue-500">
                <span class="ml-2 text-sm text-gray-700">Infrastructure</span>
            </label>
        </div>
    </fieldset>
</div>
```

### Radio Button Group
```html
<div class="mb-4">
    <fieldset>
        <legend class="block text-sm font-medium text-gray-700 mb-3">
            Development Status
        </legend>
        <div class="space-y-2">
            <label class="flex items-center">
                <input type="radio" 
                       name="status" 
                       value="developing"
                       class="h-4 w-4 text-blue-600 border-gray-300 
                              focus:ring-blue-500">
                <span class="ml-2 text-sm text-gray-700">Developing</span>
            </label>
            <label class="flex items-center">
                <input type="radio" 
                       name="status" 
                       value="established"
                       class="h-4 w-4 text-blue-600 border-gray-300 
                              focus:ring-blue-500">
                <span class="ml-2 text-sm text-gray-700">Established</span>
            </label>
            <label class="flex items-center">
                <input type="radio" 
                       name="status" 
                       value="thriving"
                       class="h-4 w-4 text-blue-600 border-gray-300 
                              focus:ring-blue-500">
                <span class="ml-2 text-sm text-gray-700">Thriving</span>
            </label>
        </div>
    </fieldset>
</div>
```

### Form with Submit Row
```html
<form class="bg-white rounded-xl shadow-lg p-6">
    <!-- Form fields here -->
    
    <div class="flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-3 pt-6 border-t border-gray-200">
        <button type="button" 
                class="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg 
                       hover:bg-gray-50 transition-colors duration-200">
            Cancel
        </button>
        <button type="submit" 
                class="bg-bangsamoro-gradient text-white px-6 py-3 rounded-lg 
                       font-semibold hover:transform hover:translate-y-[-1px] 
                       hover:shadow-lg transition-all duration-300">
            <i class="fas fa-save mr-2"></i>
            Save Changes
        </button>
    </div>
</form>
```

## Cards

### Basic Card
```html
<div class="bg-white rounded-xl shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow duration-300">
    <h3 class="text-lg font-semibold text-gray-800 mb-3">
        <i class="fas fa-users text-blue-600 mr-2"></i>
        Community Profile
    </h3>
    <p class="text-gray-600 mb-4">
        Overview of community demographics and basic information.
    </p>
    <div class="flex justify-between items-center">
        <span class="text-sm text-gray-500">Last updated: March 2024</span>
        <a href="#" class="text-blue-600 hover:text-blue-800 font-medium">
            View Details →
        </a>
    </div>
</div>
```

### Gradient Card
```html
<div class="card-gradient rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow duration-300">
    <div class="flex items-start justify-between">
        <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-2">
                Assessment Report
            </h3>
            <p class="text-gray-600 text-sm">
                Latest community needs assessment findings
            </p>
        </div>
        <div class="bg-blue-100 p-3 rounded-lg">
            <i class="fas fa-chart-line text-blue-600 text-xl"></i>
        </div>
    </div>
    <div class="mt-4">
        <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200">
            Download Report
        </button>
    </div>
</div>
```

### Stat Card
```html
<div class="bg-white rounded-xl shadow-md p-6 text-center hover:shadow-lg transition-shadow duration-300">
    <div class="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
        <i class="fas fa-home text-green-600 text-2xl"></i>
    </div>
    <h3 class="text-2xl font-bold text-gray-800 mb-1">1,247</h3>
    <p class="text-gray-600 text-sm font-medium">Total Households</p>
    <div class="mt-3 flex items-center justify-center text-green-600">
        <i class="fas fa-arrow-up text-xs mr-1"></i>
        <span class="text-xs font-medium">+12% from last month</span>
    </div>
</div>
```

### Card with Actions
```html
<div class="bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300">
    <div class="p-6">
        <div class="flex items-start justify-between mb-4">
            <div>
                <h3 class="text-lg font-semibold text-gray-800">
                    Barangay Maluso
                </h3>
                <p class="text-sm text-gray-600">Municipality of Balabagan, Lanao del Sur</p>
            </div>
            <span class="px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                Active
            </span>
        </div>
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
                <span class="text-sm text-gray-500">Population</span>
                <p class="font-semibold">2,847</p>
            </div>
            <div>
                <span class="text-sm text-gray-500">Households</span>
                <p class="font-semibold">456</p>
            </div>
        </div>
    </div>
    <div class="bg-gray-50 px-6 py-3">
        <div class="flex space-x-3">
            <button class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                <i class="fas fa-eye mr-1"></i>
                View
            </button>
            <button class="text-green-600 hover:text-green-800 text-sm font-medium">
                <i class="fas fa-edit mr-1"></i>
                Edit
            </button>
            <button class="text-purple-600 hover:text-purple-800 text-sm font-medium">
                <i class="fas fa-chart-bar mr-1"></i>
                Report
            </button>
        </div>
    </div>
</div>
```

## Navigation

### Breadcrumb
```html
<nav class="flex mb-6" aria-label="Breadcrumb">
    <ol class="flex items-center space-x-2 text-sm">
        <li>
            <a href="/" class="text-blue-600 hover:text-blue-800">
                <i class="fas fa-home"></i>
            </a>
        </li>
        <li class="flex items-center">
            <i class="fas fa-chevron-right text-gray-400 mx-2"></i>
            <a href="/communities" class="text-blue-600 hover:text-blue-800">Communities</a>
        </li>
        <li class="flex items-center">
            <i class="fas fa-chevron-right text-gray-400 mx-2"></i>
            <span class="text-gray-700">Barangay Profile</span>
        </li>
    </ol>
</nav>
```

### Tab Navigation
```html
<div class="border-b border-gray-200 mb-6">
    <nav class="-mb-px flex space-x-8">
        <a href="#overview" 
           class="border-b-2 border-blue-500 text-blue-600 py-2 px-1 text-sm font-medium">
            Overview
        </a>
        <a href="#demographics" 
           class="border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 py-2 px-1 text-sm font-medium">
            Demographics
        </a>
        <a href="#infrastructure" 
           class="border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 py-2 px-1 text-sm font-medium">
            Infrastructure
        </a>
        <a href="#stakeholders" 
           class="border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 py-2 px-1 text-sm font-medium">
            Stakeholders
        </a>
    </nav>
</div>
```

### Pagination
```html
<div class="flex items-center justify-between bg-white px-4 py-3 border border-gray-200 rounded-lg">
    <div class="flex items-center text-sm text-gray-700">
        <span>Showing</span>
        <span class="font-medium mx-1">1</span>
        <span>to</span>
        <span class="font-medium mx-1">20</span>
        <span>of</span>
        <span class="font-medium mx-1">157</span>
        <span>results</span>
    </div>
    <div class="flex items-center space-x-2">
        <button class="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50" disabled>
            Previous
        </button>
        <button class="px-3 py-2 text-sm font-medium text-white bg-blue-600 border border-blue-600 rounded-md hover:bg-blue-700">
            1
        </button>
        <button class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            2
        </button>
        <button class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            3
        </button>
        <span class="px-3 py-2 text-sm font-medium text-gray-500">...</span>
        <button class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            8
        </button>
        <button class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
            Next
        </button>
    </div>
</div>
```

## Alerts & Messages

### Success Alert
```html
<div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-check-circle text-green-400"></i>
        </div>
        <div class="ml-3">
            <h3 class="text-sm font-medium text-green-800">
                Successfully saved!
            </h3>
            <div class="mt-2 text-sm text-green-700">
                <p>Community profile has been updated successfully.</p>
            </div>
        </div>
        <div class="ml-auto pl-3">
            <button class="bg-green-50 rounded-md p-1.5 text-green-500 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-green-600 focus:ring-offset-2 focus:ring-offset-green-50">
                <i class="fas fa-times"></i>
            </button>
        </div>
    </div>
</div>
```

### Error Alert
```html
<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-exclamation-circle text-red-400"></i>
        </div>
        <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">
                There were errors with your submission
            </h3>
            <div class="mt-2 text-sm text-red-700">
                <ul class="list-disc pl-5 space-y-1">
                    <li>Community name is required</li>
                    <li>Population must be a positive number</li>
                </ul>
            </div>
        </div>
    </div>
</div>
```

### Warning Alert
```html
<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-exclamation-triangle text-yellow-400"></i>
        </div>
        <div class="ml-3">
            <h3 class="text-sm font-medium text-yellow-800">
                Attention needed
            </h3>
            <div class="mt-2 text-sm text-yellow-700">
                <p>This community data was last updated 6 months ago. Consider updating the information.</p>
            </div>
            <div class="mt-4">
                <div class="-mx-2 -my-1.5 flex">
                    <button class="bg-yellow-50 px-2 py-1.5 rounded-md text-sm font-medium text-yellow-800 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-yellow-600 focus:ring-offset-2 focus:ring-offset-yellow-50">
                        Update Now
                    </button>
                    <button class="ml-3 bg-yellow-50 px-2 py-1.5 rounded-md text-sm font-medium text-yellow-800 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-yellow-600 focus:ring-offset-2 focus:ring-offset-yellow-50">
                        Dismiss
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
```

### Info Alert
```html
<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
    <div class="flex">
        <div class="flex-shrink-0">
            <i class="fas fa-info-circle text-blue-400"></i>
        </div>
        <div class="ml-3">
            <h3 class="text-sm font-medium text-blue-800">
                New feature available
            </h3>
            <div class="mt-2 text-sm text-blue-700">
                <p>You can now export community data to various formats including PDF and Excel.</p>
            </div>
        </div>
    </div>
</div>
```

## Tables

### Basic Data Table
```html
<div class="bg-white shadow-md rounded-lg overflow-hidden">
    <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-bangsamoro-gradient">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Community
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Municipality
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Population
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                    Actions
                </th>
            </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            <tr class="hover:bg-gray-50 transition-colors duration-200">
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">Barangay Maluso</div>
                    <div class="text-sm text-gray-500">Community ID: OBC-001</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    Balabagan, Lanao del Sur
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    2,847
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Established
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex space-x-2">
                        <a href="#" class="text-blue-600 hover:text-blue-900">
                            <i class="fas fa-eye"></i>
                        </a>
                        <a href="#" class="text-green-600 hover:text-green-900">
                            <i class="fas fa-edit"></i>
                        </a>
                        <a href="#" class="text-purple-600 hover:text-purple-900">
                            <i class="fas fa-chart-bar"></i>
                        </a>
                    </div>
                </td>
            </tr>
            <!-- More rows... -->
        </tbody>
    </table>
</div>
```

### Table with Search and Filter
```html
<div class="bg-white shadow-md rounded-lg p-6 mb-6">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
        <h2 class="text-lg font-semibold text-gray-900 mb-2 sm:mb-0">
            Community List
        </h2>
        <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 w-full sm:w-auto">
            <div class="relative">
                <input type="text" 
                       placeholder="Search communities..." 
                       class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <i class="fas fa-search text-gray-400"></i>
                </div>
            </div>
            <select class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <option value="">All Regions</option>
                <option value="region-ix">Region IX</option>
                <option value="region-xii">Region XII</option>
            </select>
            <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200">
                <i class="fas fa-filter mr-2"></i>
                Filter
            </button>
        </div>
    </div>
    
    <!-- Table content here -->
</div>
```

## Status Indicators

### Status Badges
```html
<!-- Success/Positive Status -->
<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
    <i class="fas fa-check-circle mr-1"></i>
    Active
</span>

<!-- Warning Status -->
<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
    <i class="fas fa-exclamation-triangle mr-1"></i>
    Pending
</span>

<!-- Error/Negative Status -->
<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
    <i class="fas fa-times-circle mr-1"></i>
    Inactive
</span>

<!-- Info Status -->
<span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
    <i class="fas fa-info-circle mr-1"></i>
    In Review
</span>
```

### Progress Indicators
```html
<!-- Progress Bar -->
<div class="mb-4">
    <div class="flex justify-between text-sm text-gray-600 mb-1">
        <span>Assessment Progress</span>
        <span>75%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="bg-blue-600 h-2 rounded-full" style="width: 75%"></div>
    </div>
</div>

<!-- Multi-step Progress -->
<div class="flex items-center justify-between mb-8">
    <div class="flex items-center">
        <div class="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full">
            <i class="fas fa-check text-sm"></i>
        </div>
        <span class="ml-2 text-sm font-medium text-gray-900">Basic Info</span>
    </div>
    <div class="flex-1 h-1 bg-blue-600 mx-4"></div>
    <div class="flex items-center">
        <div class="flex items-center justify-center w-8 h-8 bg-blue-600 text-white rounded-full">
            2
        </div>
        <span class="ml-2 text-sm font-medium text-gray-900">Demographics</span>
    </div>
    <div class="flex-1 h-1 bg-gray-300 mx-4"></div>
    <div class="flex items-center">
        <div class="flex items-center justify-center w-8 h-8 bg-gray-300 text-gray-600 rounded-full">
            3
        </div>
        <span class="ml-2 text-sm font-medium text-gray-500">Infrastructure</span>
    </div>
</div>
```

## Layout Components

### Grid Layout
```html
<!-- 3-Column Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
    <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="font-semibold mb-2">Column 1</h3>
        <p class="text-gray-600">Content for first column</p>
    </div>
    <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="font-semibold mb-2">Column 2</h3>
        <p class="text-gray-600">Content for second column</p>
    </div>
    <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="font-semibold mb-2">Column 3</h3>
        <p class="text-gray-600">Content for third column</p>
    </div>
</div>
```

### Sidebar Layout
```html
<div class="flex flex-col lg:flex-row gap-6">
    <!-- Sidebar -->
    <div class="lg:w-1/4">
        <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="font-semibold mb-4">Filters</h3>
            <!-- Filter content -->
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="lg:w-3/4">
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold mb-4">Main Content</h2>
            <!-- Main content -->
        </div>
    </div>
</div>
```

### Section Container
```html
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Page Title</h1>
        <p class="text-gray-600">Page description or subtitle</p>
    </div>
    
    <!-- Page content -->
</div>
```

---

## Usage Notes

### Adding Icons
Most components use Font Awesome icons. Include the CDN in your base template:
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

### Color Customization
All components use CSS custom properties. Customize colors by modifying the values in your base template:
```css
:root {
    --primary-blue: #1e40af;
    --primary-teal: #059669;
    /* ... other colors */
}
```

### Responsive Considerations
- All components are mobile-first responsive
- Test components across different screen sizes
- Use appropriate breakpoint classes (sm:, md:, lg:, xl:)

### Accessibility Checklist
- [ ] Include proper ARIA labels and roles
- [ ] Ensure keyboard navigation works
- [ ] Check color contrast ratios
- [ ] Add focus indicators for interactive elements
- [ ] Use semantic HTML elements

---

*For more information, see the [UI Design System Guide](ui-design-system.md) and [Admin Interface Guide](admin-interface-guide.md)*

*Last Updated: {{ current_date }}*
*Version: 1.0*