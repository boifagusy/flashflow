"""
Hardware Integration Demo
Demonstrates the capabilities of FlashFlow's hardware integration services
"""

import sys
import os

# Add the current directory to the path so we can import the services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flashflow_cli.services.iot_service import iot_service
from flashflow_cli.services.industrial_service import industrial_service
from flashflow_cli.services.pos_service import pos_service
from flashflow_cli.services.telecom_service import telecom_service
from flashflow_cli.services.scientific_service import scientific_service


def demo_iot():
    """Demonstrate IoT device management capabilities"""
    print("=== IoT Device Management Demo ===")
    
    # Register a new IoT device
    device_id = iot_service.register_device(
        name="Temperature Sensor",
        device_type="sensor",
        protocol="MQTT"
    )
    print(f"Registered device with ID: {device_id}")
    
    # Get device information
    device = iot_service.get_device(device_id)
    print(f"Device info: {device['name']} ({device['device_type']})")
    
    # Record telemetry data
    iot_service.record_telemetry(
        device_id=device_id,
        data={
            "temperature": 23.5,
            "humidity": 65.2,
            "pressure": 1013.25
        }
    )
    print("Recorded telemetry data")
    
    # Send a command to the device
    command_id = iot_service.send_command(
        device_id=device_id,
        command="set_sampling_rate",
        parameters={"rate": 1000}
    )
    print(f"Sent command with ID: {command_id}")
    
    # List all devices
    devices = iot_service.list_devices()
    print(f"Total devices: {len(devices)}")
    print()


def demo_industrial():
    """Demonstrate industrial control system capabilities"""
    print("=== Industrial Control Systems Demo ===")
    
    # Register an industrial device
    device_id = industrial_service.register_device(
        name="PLC Controller",
        protocol="Modbus",
        ip_address="192.168.1.100",
        port=502
    )
    print(f"Registered device with ID: {device_id}")
    
    # Add a tag for data access
    industrial_service.add_tag(
        device_id=device_id,
        tag_name="motor_speed",
        tag_address="40001",
        data_type="float"
    )
    print("Added tag: motor_speed")
    
    # Read a tag value (will return None in this demo since we're not actually connected)
    speed = industrial_service.read_tag(device_id, "motor_speed")
    print(f"Read tag value: {speed}")
    
    # Write a tag value
    industrial_service.write_tag(device_id, "motor_speed", 1500.0)
    print("Wrote tag value: 1500.0")
    
    # List all devices
    devices = industrial_service.list_devices()
    print(f"Total devices: {len(devices)}")
    print()


def demo_pos():
    """Demonstrate point-of-sale system capabilities"""
    print("=== Point-of-Sale Systems Demo ===")
    
    # Register a POS terminal
    terminal_id = pos_service.register_terminal(
        name="Checkout Counter 1",
        terminal_type="checkout",
        location="Store Floor"
    )
    print(f"Registered terminal with ID: {terminal_id}")
    
    # Add inventory items
    pos_service.add_inventory_item(
        sku="PRD-001",
        name="FlashFlow T-Shirt",
        price=29.99,
        category="Apparel",
        stock_quantity=100
    )
    print("Added inventory item: FlashFlow T-Shirt")
    
    pos_service.add_inventory_item(
        sku="PRD-002",
        name="FlashFlow Mug",
        price=14.99,
        category="Merchandise",
        stock_quantity=50
    )
    print("Added inventory item: FlashFlow Mug")
    
    # Process a transaction
    transaction_id = pos_service.process_transaction(
        terminal_id=terminal_id,
        items=[
            {"sku": "PRD-001", "quantity": 2, "price": 29.99},
            {"sku": "PRD-002", "quantity": 1, "price": 14.99}
        ],
        payment_method="credit_card",
        total_amount=74.97
    )
    print(f"Processed transaction with ID: {transaction_id}")
    
    # List all terminals
    terminals = pos_service.list_terminals()
    print(f"Total terminals: {len(terminals)}")
    
    # List inventory
    inventory = pos_service.list_inventory()
    print(f"Total inventory items: {len(inventory)}")
    print()


def demo_telecom():
    """Demonstrate telecommunications equipment capabilities"""
    print("=== Telecommunications Equipment Demo ===")
    
    # Register telecommunications equipment
    equipment_id = telecom_service.register_equipment(
        name="5G Base Station",
        equipment_type="base_station",
        vendor="NetworkVendor",
        model="5G-BS-1000"
    )
    print(f"Registered equipment with ID: {equipment_id}")
    
    # Create a network
    network_id = telecom_service.create_network(
        name="5G Network",
        network_type="5G",
        frequency_band="3.5GHz"
    )
    print(f"Created network with ID: {network_id}")
    
    # Add equipment to network
    telecom_service.add_equipment_to_network(network_id, equipment_id)
    print("Added equipment to network")
    
    # Establish a connection
    connection_id = telecom_service.establish_connection(
        source_id=equipment_id,
        destination_id="router-001",
        connection_type="data"
    )
    print(f"Established connection with ID: {connection_id}")
    
    # Monitor signal quality
    telecom_service.monitor_signal(
        equipment_id=equipment_id,
        signal_strength=-75.5,
        signal_quality=92.3
    )
    print("Monitored signal quality")
    
    # List all equipment
    equipment = telecom_service.list_equipment()
    print(f"Total equipment: {len(equipment)}")
    
    # List all networks
    networks = telecom_service.list_networks()
    print(f"Total networks: {len(networks)}")
    print()


def demo_scientific():
    """Demonstrate scientific instrument capabilities"""
    print("=== Scientific Instruments Demo ===")
    
    # Register a scientific instrument
    instrument_id = scientific_service.register_instrument(
        name="UV-Vis Spectrometer",
        instrument_type="spectrometer",
        vendor="ScientificVendor",
        model="UV-2600"
    )
    print(f"Registered instrument with ID: {instrument_id}")
    
    # Create an experiment
    experiment_id = scientific_service.create_experiment(
        name="Protein Analysis",
        description="Analysis of protein concentration using Bradford assay",
        researcher="Dr. Smith",
        project="Biochemistry Research"
    )
    print(f"Created experiment with ID: {experiment_id}")
    
    # Add instrument to experiment
    scientific_service.add_instrument_to_experiment(experiment_id, instrument_id)
    print("Added instrument to experiment")
    
    # Start the experiment
    scientific_service.start_experiment(experiment_id)
    print("Started experiment")
    
    # Record measurements
    measurement_id = scientific_service.record_measurement(
        experiment_id=experiment_id,
        instrument_id=instrument_id,
        measurement_type="absorbance",
        value=0.75,
        unit="AU",
        metadata={"wavelength": 595, "dilution_factor": 1}
    )
    print(f"Recorded measurement with ID: {measurement_id}")
    
    # Calibrate instrument
    calibration_id = scientific_service.calibrate_instrument(
        instrument_id=instrument_id,
        calibration_data={
            "technician": "Lab Technician",
            "slope": 1.005,
            "intercept": 0.001,
            "next_due": "2024-12-31"
        }
    )
    print(f"Calibrated instrument with ID: {calibration_id}")
    
    # List all instruments
    instruments = scientific_service.list_instruments()
    print(f"Total instruments: {len(instruments)}")
    
    # List all experiments
    experiments = scientific_service.list_experiments()
    print(f"Total experiments: {len(experiments)}")
    print()


def main():
    """Run all demos"""
    print("FlashFlow Hardware Integration Demo")
    print("==================================")
    print()
    
    try:
        demo_iot()
        demo_industrial()
        demo_pos()
        demo_telecom()
        demo_scientific()
        
        print("All demos completed successfully!")
    except Exception as e:
        print(f"Error during demo: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())