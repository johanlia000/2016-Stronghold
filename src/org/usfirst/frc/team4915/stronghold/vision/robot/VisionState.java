package org.usfirst.frc.team4915.stronghold.vision.robot;

import edu.wpi.first.wpilibj.NamedSendable;
import edu.wpi.first.wpilibj.tables.ITable;
import edu.wpi.first.wpilibj.tables.ITableListener;

/*
 * The VisionState class provides access within the Robot and the
 * driver station to the values produced by the vision system. 
 */

public class VisionState implements NamedSendable {
	private static VisionState s_instance;

	public synchronized static VisionState getInstance() {
		if (s_instance == null)
			s_instance = new VisionState();
		return s_instance;
	}

	public String DriverRequest;
	public int FPS = 0;
	public int TargetsAcquired = 0;
	public int TargetX = 0;
	public int TargetY = 0;
	public int TargetSize = 0;
	public double TargetResponse = 0;
	public int TargetClass = 0;

	private ITable m_table = null;
	private final ITableListener m_listener = new ITableListener() {
		@Override
		public void valueChanged(ITable table, String key, Object value, boolean isNew) {
			/*
			 * All numbers are stored as doubles in the network tables, event
			 * those posted as int, float.
			 */
			if (key == "DriverRequest")
				s_instance.DriverRequest = (String) value;
			else {
				double num = ((Double) value).doubleValue();
				int ival = (int) num;
				if (key == "FPS")
					s_instance.FPS = ival;
				else if (key == "TargetsAcquired")
					s_instance.TargetsAcquired = ival;
				else if (key == "TargetX")
					s_instance.TargetX = ival;
				else if (key == "TargetY")
					s_instance.TargetY = ival;
				else if (key == "TargetSize")
					s_instance.TargetSize = ival;
				else if (key == "TargetResponse")
					s_instance.TargetResponse = num;
				else if (key == "TargetClass")
					s_instance.TargetClass = ival;
			}
		}
	};

	/** constructor is private, we're singleton for now */
	private VisionState() {
	}

	public String getName() {
		return "Vision";
	}

	public ITable getTable() {
		return m_table;
	}

	public String getSmartDashboardType() {
		return "Vision";
	}

	public void initTable(ITable subtable) {
		if (this.m_table != null)
			this.m_table.removeTableListener(m_listener);
		this.m_table = subtable;
		m_table.addTableListenerEx(m_listener, ITable.NOTIFY_NEW | ITable.NOTIFY_IMMEDIATE);

		this.DriverRequest = m_table.getString("DriverRequest", "init");
		this.FPS = (int) m_table.getNumber("FPS", 0.);
		this.TargetsAcquired = (int) m_table.getNumber("TargetsAcquired", 0);
		this.TargetX = (int) m_table.getNumber("TargetX", 0);
		this.TargetY = (int) m_table.getNumber("TargetY", 0);
		this.TargetSize = (int) m_table.getNumber("TargetSize", 0);
		this.TargetResponse = m_table.getNumber("TargetResponse", 0.);
		this.TargetClass = (int) m_table.getNumber("TargetClass", 0);

	}
}
