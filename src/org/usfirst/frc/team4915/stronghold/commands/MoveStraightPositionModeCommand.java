package org.usfirst.frc.team4915.stronghold.commands;

import edu.wpi.first.wpilibj.CANTalon;
import edu.wpi.first.wpilibj.command.Command;
import org.usfirst.frc.team4915.stronghold.Robot;
import org.usfirst.frc.team4915.stronghold.subsystems.DriveTrain;

import java.util.ArrayList;
import java.util.List;

public class MoveStraightPositionModeCommand extends Command {

    public static List<CANTalon> motors = Robot.driveTrain.motors;
    public double inputDistanceInches;
    private DriveTrain driveTrain = Robot.driveTrain;
    private List<Double> desiredTicksValue;
    private double driveStraightValue =  0.7;

    public MoveStraightPositionModeCommand(double inputDistanceInches) {

        requires(this.driveTrain);

        System.out.println("***MoveStraightPositionModeCommand inputDistance: " + inputDistanceInches + "*******");
        //input of the distance is in inc
        this.inputDistanceInches = inputDistanceInches;

        // Use requires() here to declare subsystem dependencies
        // eg. requires(chassis);
    }

    // Called just before this Command runs the first time

    /**
     * This initializes the variables for the distance calculator.
     */
    @Override
    protected void initialize() {
        this.desiredTicksValue = new ArrayList<Double>();

        double ticksToMove = (this.inputDistanceInches * 256 * 4) / (14 * Math.PI);
        
        double startingTickValue; 
        double endValue; 
        // get the starting encoder value
        // move motors and read new encoder value
        for (int i = 0; i < motors.size(); i++) {
            CANTalon motor = motors.get(i);
            startingTickValue = motors.get(i).getPosition();
            endValue = startingTickValue + ticksToMove;
            
            //checking if it's the right side motors
            //right side motors are the 2,3 (left are 0,1)
            if (i >= 2) {
                // right motors are inverted
                endValue = startingTickValue - ticksToMove;
            }
            this.desiredTicksValue.add(endValue);
        }
        
    }

    /**
     * This uses the wheel circumference and the number of rotations to compute
     * the distance traveled.
     */

    // Called repeatedly when this Command is scheduled to run
    @Override
    protected void execute() {
        if (this.inputDistanceInches < 0) {
            this.driveTrain.driveStraight(this.driveStraightValue);
        } else {
            this.driveTrain.driveStraight(-this.driveStraightValue);
        }
    }

    // Make this return true when this Command no longer needs to run execute()
    @Override
    protected boolean isFinished() {
        // checking to see if the front motors have finished regardless of
        // driving direction
        System.out.println("input distance in inches: " + inputDistanceInches);
        if (this.inputDistanceInches > 0) {
            return isMotorFinished(1) || isMotorFinished(3);
        } else {
            return isMotorFinished(0) || isMotorFinished(2);
        }
    }

    private boolean isMotorFinished(int i) {
        boolean finished = false;
        double desiredPosition = this.desiredTicksValue.get(i);
        
        if (i >= 2) {
            double currentPosition = motors.get(i).getPosition();
            System.out.println("Motor " + i + ": current position: " + currentPosition + ", desired position " + desiredPosition);

            // right motors are inverted
            if (this.inputDistanceInches < 0) {
                finished = currentPosition >= desiredPosition;
            } else {
                finished = currentPosition <= desiredPosition;
            }
        } else {
            double currentPosition = motors.get(i).getPosition();
            System.out.println("Motor " + i + ": current position: " + currentPosition + ", desired position " + desiredPosition);
            if (this.inputDistanceInches < 0) {
                finished = currentPosition <= desiredPosition;
            } else {
                finished = currentPosition >= desiredPosition;
            }
        }
        if (finished){
            System.out.println("Motor " + i + " finished");
        }
        return finished;

    }

    // Called once after isFinished returns true
    @Override
    protected void end() {
        this.driveTrain.robotDrive.stopMotor();
    }

    // Called when another command which requires one or more of the same
    // subsystems is scheduled to run
    @Override
    protected void interrupted() {
        end();
    }
}
