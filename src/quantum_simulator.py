"""
Quantum Simulator for Multiverse Spectrum Analyzer

This module provides the core quantum mechanics simulation functionality
for the Multiverse Spectrum Analyzer. It implements wave function calculations,
universe branching logic, and probability distributions based on the
Many-Worlds Interpretation of quantum mechanics.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as colors
from mpl_toolkits.mplot3d import Axes3D

class QuantumState:
    """
    Represents a quantum state with wave function and probability distribution.
    """
    def __init__(self, dimensions=1, resolution=100, bounds=(-5, 5)):
        """
        Initialize a quantum state.
        
        Args:
            dimensions: Number of dimensions for the quantum state
            resolution: Number of points to sample in each dimension
            bounds: Tuple of (min, max) values for each dimension
        """
        self.dimensions = dimensions
        self.resolution = resolution
        self.bounds = bounds
        
        # Create coordinate grid
        if dimensions == 1:
            self.x = np.linspace(bounds[0], bounds[1], resolution)
            self.grid = self.x
        elif dimensions == 2:
            self.x = np.linspace(bounds[0], bounds[1], resolution)
            self.y = np.linspace(bounds[0], bounds[1], resolution)
            self.X, self.Y = np.meshgrid(self.x, self.y)
            self.grid = (self.X, self.Y)
        
        # Initialize wave function to ground state (Gaussian)
        self.initialize_wave_function()
    
    def initialize_wave_function(self, state_type="ground"):
        """
        Initialize the wave function to a specific state.
        
        Args:
            state_type: Type of initial state ("ground", "excited", "superposition")
        """
        if state_type == "ground":
            if self.dimensions == 1:
                # 1D Gaussian ground state
                self.psi = np.exp(-self.x**2 / 2) / np.sqrt(np.pi)
            elif self.dimensions == 2:
                # 2D Gaussian ground state
                self.psi = np.exp(-(self.X**2 + self.Y**2) / 2) / np.sqrt(np.pi)
        
        elif state_type == "excited":
            if self.dimensions == 1:
                # 1D first excited state (Hermite polynomial * Gaussian)
                self.psi = self.x * np.exp(-self.x**2 / 2) / np.sqrt(np.pi)
            elif self.dimensions == 2:
                # 2D first excited state
                self.psi = (self.X**2 + self.Y**2) * np.exp(-(self.X**2 + self.Y**2) / 2) / np.sqrt(np.pi)
        
        elif state_type == "superposition":
            # Superposition of ground and excited states
            self.initialize_wave_function("ground")
            ground = self.psi.copy()
            
            self.initialize_wave_function("excited")
            excited = self.psi.copy()
            
            # Create superposition with complex coefficients
            self.psi = (ground + 1j * excited) / np.sqrt(2)
    
    def get_probability_density(self):
        """
        Calculate the probability density from the wave function.
        
        Returns:
            Probability density array
        """
        return np.abs(self.psi)**2
    
    def normalize(self):
        """
        Normalize the wave function to ensure total probability is 1.
        """
        if self.dimensions == 1:
            norm = np.sqrt(np.sum(np.abs(self.psi)**2) * (self.bounds[1] - self.bounds[0]) / self.resolution)
        elif self.dimensions == 2:
            dx = (self.bounds[1] - self.bounds[0]) / self.resolution
            norm = np.sqrt(np.sum(np.abs(self.psi)**2) * dx**2)
        
        self.psi = self.psi / norm
    
    def evolve(self, time_step=0.1):
        """
        Evolve the wave function in time according to the Schrödinger equation.
        
        Args:
            time_step: Time step for evolution
        """
        # Simple time evolution for demonstration
        # In a real simulation, we would use a proper Hamiltonian
        if self.dimensions == 1:
            # Apply phase rotation based on "energy"
            energy_factor = np.linspace(0, 5, self.resolution)
            phase = np.exp(-1j * energy_factor * time_step)
            self.psi = self.psi * phase
        elif self.dimensions == 2:
            # 2D evolution with position-dependent phase
            energy_factor = self.X**2 + self.Y**2
            phase = np.exp(-1j * energy_factor * time_step)
            self.psi = self.psi * phase
        
        self.normalize()


class MultiverseBranch:
    """
    Represents a branch in the multiverse, containing a quantum state
    and information about its relationship to other branches.
    """
    def __init__(self, quantum_state=None, parent=None, branch_probability=1.0):
        """
        Initialize a multiverse branch.
        
        Args:
            quantum_state: The quantum state of this branch
            parent: Parent branch (None for the root branch)
            branch_probability: Probability of this branch relative to its parent
        """
        self.quantum_state = quantum_state if quantum_state else QuantumState()
        self.parent = parent
        self.children = []
        self.branch_probability = branch_probability
        self.absolute_probability = branch_probability
        
        # Calculate absolute probability by multiplying with parent probabilities
        if parent:
            self.absolute_probability = parent.absolute_probability * branch_probability
    
    def add_child(self, quantum_state=None, branch_probability=0.5):
        """
        Add a child branch to this branch.
        
        Args:
            quantum_state: Quantum state for the new branch
            branch_probability: Probability of the new branch
        
        Returns:
            The newly created child branch
        """
        child = MultiverseBranch(quantum_state, self, branch_probability)
        self.children.append(child)
        return child
    
    def branch(self, num_branches=2):
        """
        Create multiple branches from this branch based on a quantum event.
        
        Args:
            num_branches: Number of branches to create
        
        Returns:
            List of newly created branches
        """
        # Equal probability for each branch by default
        probability = 1.0 / num_branches
        
        new_branches = []
        for i in range(num_branches):
            # Create a slightly modified quantum state for each branch
            new_state = QuantumState(
                dimensions=self.quantum_state.dimensions,
                resolution=self.quantum_state.resolution,
                bounds=self.quantum_state.bounds
            )
            
            # Initialize with a variation of the parent state
            if i == 0:
                new_state.initialize_wave_function("ground")
            elif i == 1:
                new_state.initialize_wave_function("excited")
            else:
                new_state.initialize_wave_function("superposition")
            
            # Add the new branch
            new_branch = self.add_child(new_state, probability)
            new_branches.append(new_branch)
        
        return new_branches


class MultiverseSimulator:
    """
    Simulates the multiverse based on quantum events and branching.
    """
    def __init__(self):
        """
        Initialize the multiverse simulator.
        """
        # Create the root branch of the multiverse
        self.root_branch = MultiverseBranch()
        self.current_branch = self.root_branch
        self.all_branches = [self.root_branch]
        self.time = 0
    
    def trigger_quantum_event(self, branch=None, num_branches=2):
        """
        Trigger a quantum event that causes universe branching.
        
        Args:
            branch: Branch where the event occurs (default: current branch)
            num_branches: Number of branches to create
        
        Returns:
            List of newly created branches
        """
        if branch is None:
            branch = self.current_branch
        
        new_branches = branch.branch(num_branches)
        self.all_branches.extend(new_branches)
        return new_branches
    
    def evolve_multiverse(self, time_step=0.1):
        """
        Evolve all branches of the multiverse in time.
        
        Args:
            time_step: Time step for evolution
        """
        self.time += time_step
        
        for branch in self.all_branches:
            branch.quantum_state.evolve(time_step)
    
    def get_branch_structure(self):
        """
        Get the structure of branches in the multiverse.
        
        Returns:
            Dictionary representing the branch structure
        """
        def build_branch_dict(branch):
            branch_dict = {
                "probability": branch.absolute_probability,
                "children": [build_branch_dict(child) for child in branch.children]
            }
            return branch_dict
        
        return build_branch_dict(self.root_branch)
    
    def visualize_probability_distribution(self, branch=None):
        """
        Visualize the probability distribution of a branch.
        
        Args:
            branch: Branch to visualize (default: current branch)
        """
        if branch is None:
            branch = self.current_branch
        
        quantum_state = branch.quantum_state
        probability = quantum_state.get_probability_density()
        
        plt.figure(figsize=(10, 6))
        
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
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/multiverse_analyzer/probability_distribution.png')
        plt.close()
    
    def visualize_wave_function_3d(self, branch=None):
        """
        Create a 3D visualization of the wave function.
        
        Args:
            branch: Branch to visualize (default: current branch)
        """
        if branch is None:
            branch = self.current_branch
        
        quantum_state = branch.quantum_state
        
        if quantum_state.dimensions == 1:
            # For 1D, create a 3D plot with real and imaginary components
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            x = quantum_state.x
            real_part = np.real(quantum_state.psi)
            imag_part = np.imag(quantum_state.psi)
            probability = quantum_state.get_probability_density()
            
            # Plot real part
            ax.plot(x, real_part, np.zeros_like(x), color='blue', label='Real Part')
            # Plot imaginary part
            ax.plot(x, np.zeros_like(x), imag_part, color='red', label='Imaginary Part')
            # Plot probability density
            ax.plot(x, np.zeros_like(x), np.zeros_like(x), probability, color='purple', label='Probability')
            
            ax.set_xlabel('Position')
            ax.set_ylabel('Real Part')
            ax.set_zlabel('Imaginary Part')
            ax.set_title('3D Visualization of Quantum Wave Function')
            ax.legend()
        
        elif quantum_state.dimensions == 2:
            # For 2D, create a surface plot of the probability density
            fig = plt.figure(figsize=(12, 10))
            ax = fig.add_subplot(111, projection='3d')
            
            X, Y = quantum_state.X, quantum_state.Y
            probability = quantum_state.get_probability_density()
            
            # Create a surface plot
            surf = ax.plot_surface(X, Y, probability, cmap='viridis', 
                                  linewidth=0, antialiased=True)
            
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Probability Density')
            ax.set_xlabel('X Position')
            ax.set_ylabel('Y Position')
            ax.set_zlabel('Probability Density')
            ax.set_title('3D Visualization of 2D Quantum Wave Function')
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/multiverse_analyzer/wave_function_3d.png')
        plt.close()
    
    def visualize_multiverse_branches(self):
        """
        Visualize the branching structure of the multiverse.
        """
        def plot_branch(branch, x, y, dx, level, ax):
            # Plot the current branch
            probability = branch.absolute_probability
            color = plt.cm.viridis(probability)
            
            # Draw branch as a line
            ax.plot([x, x + dx], [y, y + 1], color=color, linewidth=2 * probability + 1)
            
            # If this branch has children, plot them
            if branch.children:
                num_children = len(branch.children)
                new_dx = dx / num_children
                
                for i, child in enumerate(branch.children):
                    new_x = x + dx - new_dx * (num_children - i)
                    plot_branch(child, new_x, y + 1, new_dx, level + 1, ax)
        
        # Create the figure
        fig, ax = plt.figure(figsize=(12, 8)), plt.gca()
        
        # Start plotting from the root
        plot_branch(self.root_branch, 0, 0, 10, 0, ax)
        
        # Set labels and title
        ax.set_xlabel('Branch Variation')
        ax.set_ylabel('Time/Branching Events')
        ax.set_title('Multiverse Branching Structure')
        
        # Remove axis ticks for cleaner visualization
        ax.set_xticks([])
        
        plt.tight_layout()
        plt.savefig('/home/ubuntu/multiverse_analyzer/multiverse_branches.png')
        plt.close()
    
    def create_animated_evolution(self, num_frames=50, interval=100):
        """
        Create an animated visualization of quantum state evolution.
        
        Args:
            num_frames: Number of frames in the animation
            interval: Interval between frames in milliseconds
        """
        # Create a copy of the current branch for animation
        branch = MultiverseBranch()
        branch.quantum_state.initialize_wave_function("superposition")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if branch.quantum_state.dimensions == 1:
            x = branch.quantum_state.x
            line, = ax.plot([], [], lw=2)
            fill = ax.fill_between([], [], alpha=0.3, color='blue')
            
            ax.set_xlim(branch.quantum_state.bounds)
            ax.set_ylim(0, 1)
            ax.set_xlabel('Position')
            ax.set_ylabel('Probability Density')
            ax.set_title('Quantum Wave Function Evolution')
            ax.grid(True)
            
            def init():
                line.set_data([], [])
                return line,
            
            def animate(i):
                # Evolve the quantum state
                branch.quantum_state.evolve(0.1)
                probability = branch.quantum_state.get_probability_density()
                
                # Update the plot
                line.set_data(x, probability)
                
                # Update the fill - remove previous fill and create new one
                for coll in ax.collections:
                    coll.remove()
                ax.fill_between(x, 0, probability, alpha=0.3, color='blue')
                
                return line,
            
        elif branch.quantum_state.dimensions == 2:
            X, Y = branch.quantum_state.X, branch.quantum_state.Y
            
            # Initial probability distribution
            probability = branch.quantum_state.get_probability_density()
            
            # Create the initial contour plot
            contour = ax.contourf(X, Y, probability, 50, cmap='viridis')
            fig.colorbar(contour, label='Probability Density')
            
            ax.set_xlabel('X Position')
            ax.set_ylabel('Y Position')
            ax.set_title('2D Quantum Wave Function Evolution')
            
            def init():
                return contour,
            
            def animate(i):
                # Evolve the quantum state
                branch.quantum_state.evolve(0.1)
                probability = branch.quantum_state.get_probability_density()
                
                # Clear the previous contour
                for coll in ax.collections:
                    coll.remove()
                
                # Create a new contour
                contour = ax.contourf(X, Y, probability, 50, cmap='viridis')
                
                return contour,
        
        # Create the animation
        anim = FuncAnimation(fig, animate, init_func=init,
                             frames=num_frames, interval=interval, blit=True)
        
        # Save the animation
        anim.save('/home/ubuntu/multiverse_analyzer/quantum_evolution.gif', writer='pillow', fps=10)
        plt.close()


# Example usage
if __name__ == "__main__":
    # Create a multiverse simulator
    simulator = MultiverseSimulator()
    
    # Trigger some quantum events to create branches
    simulator.trigger_quantum_event(num_branches=2)
    simulator.evolve_multiverse(0.5)
    
    # Trigger more branching on one of the branches
    simulator.current_branch = simulator.all_branches[1]
    simulator.trigger_quantum_event(num_branches=3)
    simulator.evolve_multiverse(0.5)
    
    # Visualize the results
    simulator.visualize_probability_distribution()
    simulator.visualize_wave_function_3d()
    simulator.visualize_multiverse_branches()
    simulator.create_animated_evolution(num_frames=30)
    
    print("Multiverse simulation complete. Visualizations saved to the multiverse_analyzer directory.")
