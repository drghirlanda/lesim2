import matplotlib.pyplot as plt

from .testutil import LsTestCase, run, get_plot_data


class TestBasic(LsTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        plt.close('all')

    def test_plant_approach_berry(self):
        script = '''
n_subjects           : 10
mechanism            : SR
behaviors            : approach, eat, other
stimulus_elements    : plant, berry, sugar, no_reward
response_requirements: approach:plant, eat:berry
start_v              : plant->other:0, berry->other:0, default:-1
alpha_v              : 0.1
alpha_w              : 0.1
beta                 : 1
behavior_cost        : approach:1, default: 0
u                    : sugar:10, default:0
bind_trials          : on

@phase acquisition stop: plant=3000
ew_trial              | PLANT
PLANT       plant     | approach: BERRY | ew_trial
BERRY       berry     | eat: REWARD     | NO_REWARD
REWARD      sugar     | ew_trial
NO_REWARD   no_reward | ew_trial

@figure

trace: 0
@run acquisition runlabel:0

trace: 0.25
@run acquisition runlabel:0.25

trace: 0.5
@run acquisition runlabel:0.5

trace: 0.75
@run acquisition runlabel:0.75

xscale: plant
subject: average

runlabel:0
@vplot berry->eat {'label':'0'}
@vplot plant->approach {'label':'0: plant->approach'}

runlabel:0.25
@vplot berry->eat {'label':'0.25'}

runlabel:0.5
@vplot berry->eat {'label':'0.5'}
@vplot plant->approach {'label':'0.5: plant->approach'}

runlabel:0.75
@vplot berry->eat {'label':'0.75'}

@legend
'''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()

        # Check that the start values (x=0) are at (0,-1)
        for _, plot in plot_data.items():
            self.assertEqual(plot['x'][0], 0)
            self.assertEqual(plot['y'][0], -1)

        # Check that all y-values are between -1 and 10
        for _, plot in plot_data.items():
            for y in plot['y']:
                self.assertLessEqual(y, 10)
                self.assertGreaterEqual(y, -1)

        # Check that all curves are "almost" nondecreasing
        for _, plot in plot_data.items():
            y_values = plot['y']
            for i in range(1, len(y_values) - 2):  # Remove the last two because of issue #64
                if y_values[i] < y_values[i - 1]:
                    self.assertLess(y_values[i - 1] - y_values[i], 0.1)

        # Check that "0: plant->approach" is constant -1 (the start_v value)
        ypa0 = plot_data['0: plant->approach']['y']
        for y in ypa0:
            self.assertEqual(y, -1)

        # Check that "0.5: plant->approach" converges to a value between -0.5 and 0
        ypa50 = plot_data['0.5: plant->approach']['y']
        for y in ypa50:
            self.assertGreaterEqual(y, -1)
            self.assertLess(y, 0)
        ypa50_last = ypa50[-50:-2]  # The last 50 items (except the last two, because of issue #64)
        for y in ypa50_last:
            self.assertGreater(y, -0.55)
            self.assertLess(y, -0.45)
        self.assertLess(max(ypa50_last) - min(ypa50_last), 0.02)

        # Check that "0" converges to 10
        y0 = plot_data['0']['y']
        for y in y0:
            self.assertGreaterEqual(y, -1)
            self.assertLessEqual(y, 10)
        y0_last = y0[-50:-2]  # The last 50 items (except the last two, because of issue #64)
        for y in y0_last:
            self.assertGreater(y, 9.8)
        self.assertLess(max(y0_last) - min(y0_last), 0.01)

        # Check that "0.25" converges to a value between 9.2 and 9.4
        y25 = plot_data['0.25']['y']
        for y in y25:
            self.assertLess(y, 9.5)
        y25_last = y25[-50:-2]  # The last 50 items (except the last two, because of issue #64)
        for y in y25_last:
            self.assertGreater(y, 9.2)
            self.assertLess(y, 9.4)
        self.assertLess(max(y25_last) - min(y25_last), 0.01)

        # Check that "0.50" converges to a value between 6.9 and 7.2
        y50 = plot_data['0.5']['y']
        for y in y50:
            self.assertLess(y, 7.2)
        y50_last = y50[-50:-2]  # The last 50 items (except the last two, because of issue #64)
        for y in y50_last:
            self.assertGreater(y, 6.9)
        self.assertLess(max(y50_last) - min(y50_last), 0.1)

        # Check that "0.75" converges to a value between 3.4 and 3.7
        y75 = plot_data['0.75']['y']
        for y in y75:
            self.assertLess(y, 4)
        y75_last = y75[-50:-2]  # The last 50 items (except the last two, because of issue #64)
        for y in y75_last:
            self.assertGreater(y, 3.4)
            self.assertLess(y, 3.7)
        self.assertLess(max(y75_last) - min(y75_last), 0.1)

    def test_overshadowing(self):
        script = '''
n_subjects             : 10
mechanism              : SR

behaviors              : response,other
stimulus_elements      : a,b,empty,reward
start_v                : a->response:-2, b->response:-2, default:1
alpha_v                : 0.1
beta                   : 1
u                      : reward:1, default: 0

@phase Overshadowing  stop:STIMULUS=250
STIMULUS    a[0.5],b[0.5]    |response: REWARD  | STIMULUS
REWARD      reward           | STIMULUS

@phase Overshadowing_ll(Overshadowing)  stop:STIMULUS=250
STIMULUS    a[0.9],b[0.1]      |response: REWARD  | STIMULUS

@phase Overshadowing_l(Overshadowing)  stop:STIMULUS=250
STIMULUS    a[0.7],b[0.3]      |response: REWARD  | STIMULUS

@phase Overshadowing_s(Overshadowing)  stop:STIMULUS=250
STIMULUS    a[0.3],b[0.7]      |response: REWARD  | STIMULUS

@phase Overshadowing_ss(Overshadowing)  stop:STIMULUS=250
STIMULUS    a[0.1],b[0.9]      |response: REWARD  | STIMULUS

@run Overshadowing_ll  runlabel: Overshadowing_ll
@run Overshadowing_l   runlabel: Overshadowing_l
@run Overshadowing     runlabel: Overshadowing
@run Overshadowing_s   runlabel: Overshadowing_s
@run Overshadowing_ss  runlabel: Overshadowing_ss

xscale: STIMULUS
subject: average
@figure v(a->response)

@subplot 111 {'xlabel':'Trial','ylabel':'v'}

runlabel: Overshadowing_ll
@vplot a->response  {'linewidth':2,'label':'A=0.9'}

runlabel: Overshadowing_l
@vplot a->response  {'linewidth':2,'label':'A=0.7'}

runlabel: Overshadowing
@vplot a->response  {'linewidth':2,'label':'A=0.5'}

runlabel: Overshadowing_s
@vplot a->response  {'linewidth':2,'label':'A=0.3'}

runlabel: Overshadowing_ss
@vplot a->response  {'linewidth':2,'label':'A=0.1'}
@legend
'''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()

        for lbl in ['A=0.1', 'A=0.3', 'A=0.5', 'A=0.7', 'A=0.9']:
            y = plot_data[lbl]['y']
            self.assertEqual(y[0], -2)

        self.assertLess(plot_data['A=0.1']['y'][-1], plot_data['A=0.3']['y'][-1])
        self.assertLess(plot_data['A=0.3']['y'][-1], plot_data['A=0.5']['y'][-1])
        self.assertLess(plot_data['A=0.5']['y'][-1], plot_data['A=0.9']['y'][-1])

        # The overshadowing effect
        self.assertLess(plot_data['A=0.9']['y'][-1], plot_data['A=0.7']['y'][-1])

    def test_manually_extinguish_trace(self):
        script = '''
n_subjects        : 10
mechanism         : sr
behaviors         : response, no_response
stimulus_elements : background, stimulus, reward
start_v           : default:-1
alpha_v           : 0.1
u                 : reward:10, default:0

@PHASE training stop: stimulus=100
new_trial  stimulus   | response: REWARD | NO_REWARD
REWARD     reward     | new_trial
NO_REWARD  background | new_trial

@run training runlabel:no_trace

trace:0.5
@run training runlabel:trace

xscale: stimulus
subject: average
runlabel: no_trace
@figure
@vplot stimulus->response {'label':'no trace'}

runlabel: trace
@vplot stimulus->response {'label':'trace'}
@legend
'''
        script_obj, script_output = run(script)
        plot_data = get_plot_data()

        self.assertIncreasing(plot_data['no trace']['y'])
        self.assertIncreasing(plot_data['trace']['y'])

        self.assertGreater(plot_data['trace']['y'][-1], 6.5)
        self.assertLess(plot_data['trace']['y'][-1], 6.7)

        self.assertGreater(plot_data['no trace']['y'][-1], 9.9)
        self.assertLess(plot_data['no trace']['y'][-1], 10)

        self.tearDown()

        script = '''
n_subjects        : 10
mechanism         : sr
behaviors         : response, no_response, bg_response
stimulus_elements : background, stimulus, reward
response_requirements: bg_response:background
start_v           : default:-1
alpha_v           : 0.1
u                 : reward:10, default:0

@PHASE training stop: stimulus=100
EXTINGUISH  background | count_line()<100:EXTINGUISH | NEW
NEW         stimulus   | response: REWARD | NO_REWARD
REWARD      reward     | NEW
NO_REWARD   background | NEW

@run training runlabel:no_trace

trace:0.1
@run training runlabel:trace=0.1

trace:0.25
@run training runlabel:trace=0.25

trace:0.5
@run training runlabel:trace=0.5

xscale: stimulus
subject: average
runlabel: no_trace

@figure
@vplot stimulus->response {'label':'no trace'}

runlabel: trace=0.1
@vplot stimulus->response {'label':'trace=0.1'}

runlabel: trace=0.25
@vplot stimulus->response {'label':'trace=0.25'}

runlabel: trace=0.5
@vplot stimulus->response {'label':'trace=0.5'}

@legend'''

        script_obj, script_output = run(script)
        plot_data = get_plot_data()

        # Check forst and last values for all vplots
        for lbl in ['trace=0.1', 'trace=0.25', 'trace=0.5']:
            self.assertEqual(plot_data[lbl]['y'][0], -1)

            # The first time stimulus is encountered, we still haven't
            # updated v(stimulus->response) for the first time yet
            self.assertEqual(plot_data[lbl]['y'][1], -1)

            self.assertLess(plot_data[lbl]['y'][-1], 10)
            self.assertGreater(plot_data[lbl]['y'][-1], 9.8)

        # check that the smaller the trace-value, the closer to "no trace" the vplot is
        sum_of_sqares = dict()
        for lbl in ['trace=0.1', 'trace=0.25', 'trace=0.5']:
            ss = 0
            for i in range(len(plot_data[lbl]['y'])):
                ss += (plot_data['no trace']['y'][i] - plot_data[lbl]['y'][i])**2
            sum_of_sqares[lbl] = ss
        self.assertLess(sum_of_sqares['trace=0.1'], sum_of_sqares['trace=0.25'])
        self.assertLess(sum_of_sqares['trace=0.25'], sum_of_sqares['trace=0.5'])
