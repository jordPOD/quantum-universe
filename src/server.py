#!/usr/bin/env python3
"""
Web Server for Multiverse Spectrum Analyzer

This script creates a web server that connects the Python quantum simulation
backend with the HTML/JavaScript frontend interface.
"""

import os
import json
import sys
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Add the current directory to the path so we can import the quantum_simulator module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from quantum_simulator import QuantumState, MultiverseBranch, MultiverseSimulator

app = Flask(__name__, static_folder='.')

# Global simulator instance
simulator = MultiverseSimulator()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/initialize', methods=['POST'])
def initialize():
    """Initialize the simulator with user parameters"""
    data = request.json
    
    # Extract parameters from request
    dimensions = int(data.get('dimensions', 1))
    initial_state = data.get('initial_state', 'ground')
    resolution = int(data.get('resolution', 100))
    
    # Create a new simulator
    global simulator
    simulator = MultiverseSimulator()
    
    # Initialize the root branch with specified parameters
    root_state = QuantumState(
        dimensions=dimensions,
        resolution=resolution,
        bounds=(-5, 5)
    )
    root_state.initialize_wave_function(initial_state)
    
    simulator.root_branch = MultiverseBranch(root_state)
    simulator.current_branch = simulator.root_branch
    simulator.all_branches = [simulator.root_branch]
    simulator.time = 0
    
    return jsonify({
        'status': 'success',
        'message': 'Simulator initialized',
        'time': simulator.time,
        'branch_count': len(simulator.all_branches)
    })

@app.route('/api/trigger_event', methods=['POST'])
def trigger_event():
    """Trigger a quantum event that causes universe branching"""
    data = request.json
    
    # Extract parameters from request
    num_branches = int(data.get('num_branches', 2))
    branch_probability = float(data.get('branch_probability', 0.5))
    
    # Trigger the quantum event
    new_branches = simulator.trigger_quantum_event(num_branches=num_branches)
    
    # Return updated state
    return jsonify({
        'status': 'success',
        'message': f'Created {len(new_branches)} new branches',
        'time': simulator.time,
        'branch_count': len(simulator.all_branches)
    })

@app.route('/api/evolve', methods=['POST'])
def evolve():
    """Evolve the multiverse by one time step"""
    data = request.json
    
    # Extract parameters from request
    time_step = float(data.get('time_step', 0.1))
    
    # Evolve the multiverse
    simulator.evolve_multiverse(time_step)
    
    # Return updated state
    return jsonify({
        'status': 'success',
        'message': f'Evolved multiverse by {time_step} time units',
        'time': simulator.time,
        'branch_count': len(simulator.all_branches)
    })

@app.route('/api/get_probability_visualization', methods=['GET'])
def get_probability_visualization():
    """Generate and return visualization of probability distribution"""
    # Get the current branch
    branch = simulator.current_branch
    quantum_state = branch.quantum_state
    
    # Create a figure
    plt.figure(figsize=(8, 6))
    
    # Get probability density
    probability = quantum_state.get_probability_density()
    
    # Create visualization based on dimensions
    if quantum_state.dimensions == 1:
        plt.plot(quantum_state.x, probability)
        plt.fill_between(quantum_state.x, 0, probability, alpha=0.3)
        plt.xlabel('Position')
        plt.ylabel('Probability Density')
        plt.title('Quantum Probability Distribution')
        plt.grid(True)
    
    elif quantum_state.dimensions == 2:
        plt.contourf(quantum_state.X, quantum_state.Y, probability, 50, cmap='viridis')
        plt.colorbar(label='Probability Density')
        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.title('2D Quantum Probability Distribution')
    
    # Save the figure to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return jsonify({
        'status': 'success',
        'image': f'data:image/png;base64,{image_base64}',
        'dimensions': quantum_state.dimensions
    })

@app.route('/api/get_branch_visualization', methods=['GET'])
def get_branch_visualization():
    """Generate and return visualization of multiverse branches"""
    # Create a figure
    plt.figure(figsize=(10, 8))
    
    # Define a recursive function to plot branches
    def plot_branch(branch, x, y, dx, level, max_level=5):
        if level > max_level:
            return
        
        # Plot the current branch
        probability = branch.absolute_probability
        color = plt.cm.viridis(probability)
        
        # Draw branch as a line
        plt.plot([x, x + dx], [y, y + 1], color=color, linewidth=2 * probability + 1)
        
        # If this branch has children, plot them
        if branch.children:
            num_children = len(branch.children)
            new_dx = dx / num_children
            
            for i, child in enumerate(branch.children):
                new_x = x + dx - new_dx * (num_children - i)
                plot_branch(child, new_x, y + 1, new_dx, level + 1, max_level)
    
    # Start plotting from the root
    plot_branch(simulator.root_branch, 0, 0, 10, 0)
    
    # Set labels and title
    plt.xlabel('Branch Variation')
    plt.ylabel('Time/Branching Events')
    plt.title('Multiverse Branching Structure')
    
    # Remove axis ticks for cleaner visualization
    plt.xticks([])
    
    # Save the figure to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return jsonify({
        'status': 'success',
        'image': f'data:image/png;base64,{image_base64}',
        'branch_count': len(simulator.all_branches)
    })

@app.route('/api/get_spectrum_visualization', methods=['GET'])
def get_spectrum_visualization():
    """Generate and return visualization of quantum spectrum"""
    # Create a figure
    plt.figure(figsize=(10, 6))
    
    # Get all branches
    branches = simulator.all_branches
    
    # Create a spectrum-like visualization
    x = np.linspace(0, 10, 100)
    
    for i, branch in enumerate(branches):
        # Create a unique spectral line for each branch
        y = np.zeros_like(x)
        
        # Add peaks at positions based on branch characteristics
        for j in range(1, 5):
            # Use branch properties to determine peak positions and heights
            position = (i * 2.5 + j) % 10
            height = branch.absolute_probability * (5 - j) / 2
            
            # Add a Gaussian peak
            y += height * np.exp(-(x - position)**2 / 0.1)
        
        # Plot the spectral line
        plt.plot(x, y, alpha=0.7, linewidth=1.5)
    
    # Add a highlighted line for the current branch
    current_index = branches.index(simulator.current_branch)
    y = np.zeros_like(x)
    
    for j in range(1, 5):
        position = (current_index * 2.5 + j) % 10
        height = simulator.current_branch.absolute_probability * (5 - j) / 2
        y += height * np.exp(-(x - position)**2 / 0.1)
    
    plt.plot(x, y, color='red', linewidth=2.5, label='Current Universe')
    
    # Set labels and title
    plt.xlabel('Quantum State Parameter')
    plt.ylabel('Probability Amplitude')
    plt.title('Multiverse Quantum Spectrum')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save the figure to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return jsonify({
        'status': 'success',
        'image': f'data:image/png;base64,{image_base64}'
    })

@app.route('/api/get_navigator_visualization', methods=['GET'])
def get_navigator_visualization():
    """Generate and return visualization of multiverse navigator"""
    # Create a figure
    plt.figure(figsize=(8, 8))
    
    # Create a polar plot for the navigator
    ax = plt.subplot(111, polar=True)
    
    # Get all branches
    branches = simulator.all_branches
    
    # Plot branches as points in polar coordinates
    for i, branch in enumerate(branches):
        # Calculate angle and radius based on branch properties
        angle = (i / len(branches)) * 2 * np.pi
        radius = 0.5 + branch.absolute_probability * 0.5
        
        # Plot the branch
        if branch == simulator.current_branch:
            ax.scatter(angle, radius, s=100, color='red', zorder=10)
        else:
            ax.scatter(angle, radius, s=50, color='blue', alpha=0.7)
    
    # Add connecting lines to show relationships
    def add_connections(branch, angle, radius):
        if not branch.children:
            return
        
        # Calculate angles for children
        child_indices = [branches.index(child) for child in branch.children]
        child_angles = [(idx / len(branches)) * 2 * np.pi for idx in child_indices]
        child_radii = [0.5 + child.absolute_probability * 0.5 for child in branch.children]
        
        # Draw lines to children
        for child_angle, child_radius in zip(child_angles, child_radii):
            ax.plot([angle, child_angle], [radius, child_radius], 
                   color='gray', alpha=0.5, linestyle='-', linewidth=1)
    
    # Start with the root branch
    root_index = branches.index(simulator.root_branch)
    root_angle = (root_index / len(branches)) * 2 * np.pi
    root_radius = 0.5 + simulator.root_branch.absolute_probability * 0.5
    
    # Add connections recursively
    add_connections(simulator.root_branch, root_angle, root_radius)
    
    # Set title and remove unnecessary elements
    plt.title('Multiverse Navigator')
    ax.grid(True, alpha=0.3)
    ax.set_yticklabels([])  # Remove radial ticks
    
    # Save the figure to a base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return jsonify({
        'status': 'success',
        'image': f'data:image/png;base64,{image_base64}',
        'current_branch_index': branches.index(simulator.current_branch)
    })

@app.route('/api/select_branch', methods=['POST'])
def select_branch():
    """Select a specific branch as the current branch"""
    data = request.json
    
    # Extract parameters from request
    branch_index = int(data.get('branch_index', 0))
    
    # Validate branch index
    if branch_index < 0 or branch_index >= len(simulator.all_branches):
        return jsonify({
            'status': 'error',
            'message': f'Invalid branch index: {branch_index}'
        }), 400
    
    # Set the current branch
    simulator.current_branch = simulator.all_branches[branch_index]
    
    return jsonify({
        'status': 'success',
        'message': f'Selected branch {branch_index}',
        'branch_count': len(simulator.all_branches),
        'current_branch_index': branch_index
    })

@app.route('/api/get_state', methods=['GET'])
def get_state():
    """Get the current state of the simulator"""
    return jsonify({
        'status': 'success',
        'time': simulator.time,
        'branch_count': len(simulator.all_branches),
        'current_branch_index': simulator.all_branches.index(simulator.current_branch)
    })

if __name__ == '__main__':
    # Ensure the static directory exists
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
