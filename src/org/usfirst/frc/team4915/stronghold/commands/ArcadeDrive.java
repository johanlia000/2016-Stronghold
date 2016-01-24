
package org.usfirst.frc.team4915.stronghold.commands;

import edu.wpi.first.wpilibj.Joystick;
import edu.wpi.first.wpilibj.command.Command;
import org.usfirst.frc.team4915.stronghold.Robot;

public class ArcadeDrive extends Command {

    public Joystick joystickDrive;
    private double joystickX;
    private double joystickY;
    private double joystickZ;

    public ArcadeDrive() {
        // Use requires() here to declare subsystem dependencies
        requires(Robot.driveTrain);
    }

    // Called just before this Command runs the first time
    @Override
    protected void initialize() {
    }

    // Called repeatedly when this Command is scheduled to run
    @Override
    protected void execute() {
        joystickDrive = Robot.oi.getJoystickDrive();
        
        joystickX = joystickDrive.getAxis(Joystick.AxisType.kX);
        joystickY = joystickDrive.getAxis(Joystick.AxisType.kY);
        joystickZ = joystickDrive.getAxis(Joystick.AxisType.kZ);
       
        Robot.driveTrain.joystickThrottle = Robot.driveTrain.modifyThrottle();
        //Sees if the joystick is in the middle aka stop
        if ((Math.abs(joystickX) < 0.075) && (Math.abs(joystickY) < 0.075)) {
            if(Math.abs(joystickZ) < 0.075){
                Robot.driveTrain.stop();
            }
            else{
                Robot.driveTrain.twistDrive(joystickDrive);
            }
        } else {
            Robot.driveTrain.arcadeDrive(joystickDrive);
        }

    }

    // Make this return true when this Command no longer needs to run execute()
    @Override
    protected boolean isFinished() {
        return false;
    }

    // Called once after isFinished returns true
    @Override
    protected void end() {
    }

    // Called when another command which requires one or more of the same
    // subsystems is scheduled to run
    @Override
    protected void interrupted() {
    }
}