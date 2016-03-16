package org.usfirst.frc.team4915.stronghold.subsystems;

import edu.wpi.first.wpilibj.command.Subsystem;
import org.usfirst.frc.team4915.stronghold.RobotMap;


public class Portcullis extends Subsystem {
    public static final double PERCENT_POWER = 0.6;
    // Put methods for controlling this subsystem
    // here. Call these from Commands.

    public void initDefaultCommand() {
        // Set the default command for a subsystem here.
        //setDefaultCommand(new MySpecialCommand());
    }
    
    public static void PortcullisMoveUp(){
        System.out.println("Executing move portcullis up"); 
        RobotMap.portcullisLeftMasterMotor.set(PERCENT_POWER);
        
      if (RobotMap.portcullisSwitchTop.get()){
        RobotMap.portcullisLeftMasterMotor.disableControl();
        System.out.println("Portcullis reached top");
      }
        
    }
    
    public static void PortcullisMoveDown(){
        System.out.println("Executing move portcullis down"); 
        RobotMap.portcullisLeftMasterMotor.set(-PERCENT_POWER);
        
        if (RobotMap.portcullisSwitchBottom.get()){
        RobotMap.portcullisLeftMasterMotor.disableControl();
        }
        System.out.println("Portcullis reached bottom");

    }
        
    }
        


