import getpass
import envoy
import unittest

class M2eeTest(unittest.TestCase):

    def setUp(self):
        self.mdas = ['Blank-2.5.8.mda', 'Blank-3.1.0.mda', 'Blank-4.0.0.mda']
        envoy.run('m2ee stop')

    def test_stuff(self):
        self._emptydb()
        self._verify_no_process()
        for mda in self.mdas:
            self._unpack(mda)
            print 'Testing start for \'%s\'' % mda
            self._start()
            if mda == 'Blank-4.0.0.mda': # double sync
                self._start()

            self._verify_status_running()
            self._verify_tables()
            print 'Testing stop after starting \'%s\'' % mda
            self._stop()

    def _start(self):
        envoy.run('m2ee start', data='e')
        self._verify_process()

    def _stop(self):
        self._verify_process()
        envoy.run('m2ee stop')
        self._verify_no_process()

    def _emptydb(self):
        envoy.run('m2ee emptydb', data='y')
        self._verify_no_tables()

    def _unpack(self, mda):
        print 'Testing unpack for mda \'%s\'' % mda
        self.assertFalse(envoy.run('m2ee unpack %s' % mda, data="y").std_err)

    def _verify_tables(self):
        tables = envoy.run('psql', data= '\dt')

        self.assertTrue('administration$account' in tables.std_out)

    def _verify_no_tables(self):
        tables = envoy.run('psql', data= '\dt')
        self.assertEqual('No relations found.\n', tables.std_out)

    def _verify_no_process(self):
        user = getpass.getuser()
        procs = envoy.run('ps -u %s' % user)
        self.assertFalse('java' in procs.std_out)

    def _verify_process(self):
        user = getpass.getuser()
        procs = envoy.run('ps -u %s' % user)
        self.assertTrue('java' in procs.std_out)

    def _verify_status_running(self):
        status = envoy.run('m2ee status').std_out
        reference_status = 'INFO: Application Name: Monitoring application\n\
INFO: The application process is running, the MxRuntime has status: running\n\
INFO: Logged in users: (0) []\n\
INFO: The application process is running, the MxRuntime has status: running\n\
INFO: Logged in users: (0) []\n'
        self.assertEqual(status, reference_status)
