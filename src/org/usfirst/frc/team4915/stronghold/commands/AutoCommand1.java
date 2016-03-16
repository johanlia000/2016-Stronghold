package org.usfirst.frc.team4915.stronghold.commands;

import org.usfirst.frc.team4915.stronghold.ModuleManager;
import org.usfirst.frc.team4915.stronghold.commands.DriveTrain.ArcadeDrive;
import org.usfirst.frc.team4915.stronghold.commands.DriveTrain.AutoRotateDegrees;
import org.usfirst.frc.team4915.stronghold.commands.IntakeLauncher.AimLauncherCommand;
import org.usfirst.frc.team4915.stronghold.commands.IntakeLauncher.AutoLaunchCommand;
import org.usfirst.frc.team4915.stronghold.commands.IntakeLauncher.LauncherGoToAngleCommand;
import org.usfirst.frc.team4915.stronghold.commands.IntakeLauncher.LauncherGoToNeutralPositionCommand;
import org.usfirst.frc.team4915.stronghold.commands.IntakeLauncher.LauncherGoToTravelPositionCommand;
import org.usfirst.frc.team4915.stronghold.commands.vision.AutoAimControlCommand;
import org.usfirst.frc.team4915.stronghold.commands.vision.AutoVisionDriveAndAim;
import org.usfirst.frc.team4915.stronghold.subsystems.Autonomous;

import edu.wpi.first.wpilibj.command.CommandGroup;
import edu.wpi.first.wpilibj.command.WaitCommand;

public class AutoCommand1 extends CommandGroup {

    private final Autonomous.Type type;
    private final Autonomous.Strat strat;
    private final Autonomous.Position position;

    public AutoCommand1(Autonomous.Type type, Autonomous.Strat strat, Autonomous.Position position) {
        this.strat = strat;
        this.position = position;
        this.type = type;
        System.out.println("Hello World");

        //launcher begin position
        if (ModuleManager.INTAKELAUNCHER_MODULE_ON){
        boolean launcherWantsTravelPosition = getLauncherBeginPosition(type);
        if(launcherWantsTravelPosition){
            System.out.println("Launcher go to position");
            addSequential(new LauncherGoToTravelPositionCommand());
        }
        else{
            System.out.println("Launcher go to position");
            addSequential(new LauncherGoToNeutralPositionCommand());
        }
        }
        
        if (ModuleManager.PORTCULLIS_MODULE_ON){
        //portcullis lifter begin position
        boolean portcullisBeginDown = getPortcullisBeginPosition(type);
        if (portcullisBeginDown){
            addSequential(new PortcullisMoveDown());
        }
        else{
            addSequential(new PortcullisMoveUp());
        }
        }
        //adding distances for total distance
        double totalDistance = (getDistance(type) + getDistancePastDefense(position));

    	switch (strat) {
        case NONE:
            break;

        case DRIVE_ACROSS:
            System.out.println("Starting Move Straight");
            addSequential(new AutoDriveStraight(totalDistance, getSpeed(type)));
            break;

		case DRIVE_SHOOT_VISION: // sets us up to use vision to shoot a high goal
            addSequential(new AutoDriveStraight(totalDistance, getSpeed(type)));
            addSequential(new AutoRotateDegrees( getTurnAngle(position)));
            addSequential(new AutoAimControlCommand(true, true));
            addSequential(new AutoVisionDriveAndAim());
            addSequential(new AutoLaunchCommand());
            break;

		case DRIVE_SHOOT_NO_VISION:
		    addSequential(new AutoDriveStraight(totalDistance, getSpeed(type)));
		    addSequential(new AutoRotateDegrees(getTurnAngle(position)));
			if (ModuleManager.INTAKELAUNCHER_MODULE_ON) {
				addParallel(new AimLauncherCommand());
				addSequential(new LauncherGoToAngleCommand(getAimAngle(position)));
				addSequential(new AutoLaunchCommand());
			}
			break;
    	}
	}
    
    public static boolean getPortcullisBeginPosition(Autonomous.Type type){
        boolean liftdown; //tells if portcullis needs to be down
        System.out.print(type);
        switch(type){
            case LOWBAR:
                liftdown = true;
                break;
            case MOAT:
                liftdown = false;
                break;
            case ROUGH_TERRAIN:
                liftdown = false;
                break;
            case ROCK_WALL:
                liftdown = false;
                break;
            case PORTCULLIS:
                liftdown = false;
                break;
            default:
                liftdown = false;
        }
        return liftdown;
            
        }
        
    public static boolean getLauncherBeginPosition(Autonomous.Type type) {
        boolean lowBar; // in inches
        System.out.println(type);
        switch (type) {
            case LOWBAR:
                lowBar = true;
                break;
            case MOAT:
                lowBar = false;
                break;
            case ROUGH_TERRAIN:
                lowBar = false;
                break;
            case ROCK_WALL:
                lowBar = false;
                break;
            case PORTCULLIS:
                lowBar = false;
                break;
            default:
                lowBar = false;
        }
        return lowBar;
    }

    public static double getAimAngle(Autonomous.Position position) {
        System.out.println(position);
        double angle = 0;
        switch (position) {
            case ONE:
                angle = 40;
                break;
            case TWO:
                angle = 40;
                break;
            case THREE:
                angle = 30;
                break;
            case FOUR:
                angle = 40;
                break;
            case FIVE:
                angle = 40;
                break;
            default:
                angle = 40;
        }
        return angle;
    }

    public static double getTurnAngle(Autonomous.Position position) {
        double degrees;
        switch (position) {
            case ONE:// low bar
                degrees = 80.4;
                break;
            case TWO:
                degrees = 41.08;
                break;
            case THREE:
                degrees = 11.95;
                break;
            case FOUR:
                degrees = -13.12; // turn left
                break;
            case FIVE:
                degrees = -57.75;
                break;
            default:
                degrees = 0;
        }
        return degrees;
    }

    // getting the distance to go after the barrier for launching
    // andalucia's math
    public static double getDistancePastDefense(Autonomous.Position position) {
        double distance;
        System.out.println(position);
        switch (position) {
            case ONE:// low bar
                distance = 38;
                break;
            case TWO:
                distance = 101.05;
                break;
            case THREE:
                distance = 74.1;
                break;
            case FOUR:
                distance = 75.09;
                break;
            case FIVE:
                distance = 104.97;
                break;
            default:
                distance = 70;
        }
        return distance;
    }

    public static int getDistance(Autonomous.Type type) {
        int distance; // in inches
        System.out.println(type);
        switch (type) {
            case LOWBAR:
                distance = 130;
                break;
            case MOAT:
                distance = 145;
                break;
            case ROUGH_TERRAIN:
                distance = 180;
                break;
            case ROCK_WALL:
                distance = 150;
                break;
            case PORTCULLIS:
                distance = 120;
                break;
            default:
                distance = 145;
        }
        return distance;
    }

    public static int getSpeed(Autonomous.Type type) {
        int speed; // in inches
        System.out.println(type);
        switch (type) {
            case LOWBAR:
                speed = 30;
                break;
            case MOAT:
                speed = 50;
                break;
            case ROUGH_TERRAIN:
                speed = 40;
                break;
            case ROCK_WALL:
                speed = -75; // negative speed: go backward
                break;
            case PORTCULLIS:
                speed = 30;
                break;
            default:
                speed = 35;
        }
        return speed;
    }

    protected boolean isFinished() {
        return super.isFinished(); // returns true if all the commands in this
                                   // group have been started and have finished
    }

    // Called once after isFinished returns true
    protected void end() {
    }

    // Called when another command which requires one or more of the same
    // subsystems is scheduled to run
    protected void interrupted() {
        end();
    }
}
