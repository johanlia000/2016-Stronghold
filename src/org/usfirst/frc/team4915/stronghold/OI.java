package org.usfirst.frc.team4915.stronghold;
import edu.wpi.first.wpilibj.Joystick;
import edu.wpi.first.wpilibj.buttons.JoystickButton;
import edu.wpi.first.wpilibj.smartdashboard.SmartDashboard;
import org.usfirst.frc.team4915.stronghold.commands.AutoRotateDegrees;
import org.usfirst.frc.team4915.stronghold.commands.MoveStraightPositionModeCommand;
import org.usfirst.frc.team4915.stronghold.commands.IntakeLauncher.IntakeBallCommandGroup;
import org.usfirst.frc.team4915.stronghold.commands.IntakeLauncher.LaunchBallCommandGroup;
import java.io.IOException;
import java.io.InputStream;
import java.util.jar.Attributes;
import java.util.jar.Manifest;



/**
 * This class handles the "operator interface", or the interactions between the
 * driver station and the robot code.
 */
public class OI {

    // Start the command when the button is released and let it run the command
    // until it is finished as determined by it's isFinished method.
    // button.whenReleased(new ExampleCommand());

    // constants, need to talk to electrical to figure out correct port values
    public static final int LAUNCHER_STICK_PORT = 1; // TODO
    public static final int LAUNCH_BALL_BUTTON_NUMBER = 2; // TODO
    public static final int INTAKE_BALL_BUTTON_NUMBER = 3; // TODO

    // create new joysticks
    public Joystick driveStick;
    public Joystick aimStick;

    // creates new buttons
    // launchBall triggers a command group with commands that ultimately will
    // shoot the ball
    // grabBall triggers a command group with commands that will get the ball
    // into the basket
    public JoystickButton launchBallButton;
    public JoystickButton grabBallButton;

    public OI() {
        this.driveStick = new Joystick(0);
        //buttons 
        SmartDashboard.putString("ArcadeDrive", "INFO: Initializing the ArcadeDrive");
        SmartDashboard.putData("Move straight position 30 inches ", new MoveStraightPositionModeCommand(30));
        SmartDashboard.putData("Rotate right 90 degrees ", new AutoRotateDegrees(false, 90));
        
        this.aimStick = new Joystick(LAUNCHER_STICK_PORT);
        this.grabBallButton = new JoystickButton(this.aimStick, INTAKE_BALL_BUTTON_NUMBER);
        this.launchBallButton = new JoystickButton(this.aimStick, LAUNCH_BALL_BUTTON_NUMBER);

        // binds commands to buttons
        this.grabBallButton.whenPressed(new IntakeBallCommandGroup());
        this.launchBallButton.whenPressed(new LaunchBallCommandGroup());

        try (InputStream manifest = getClass().getClassLoader().getResourceAsStream("META-INF/MANIFEST.MF")) {
            Attributes attributes = new Manifest(manifest).getMainAttributes();

            /* Print the attributes into form fields on the dashboard */
            SmartDashboard.putString("Code Version", attributes.getValue("Code-Version"));
            SmartDashboard.putString("Built At", attributes.getValue("Built-At"));
            SmartDashboard.putString("Built By", attributes.getValue("Built-By"));

            /* And print the attributes into the log. */
            System.out.println("Code Version: " + attributes.getValue("Code-Version"));
            System.out.println("Built At: " + attributes.getValue("Built-At"));
            System.out.println("Built By: " + attributes.getValue("Built-By"));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public Joystick getJoystickDrive() {
        return this.driveStick;
    }

}
