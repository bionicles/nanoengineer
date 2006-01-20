#ifndef GLOBALS_H_INCLUDED
#define GLOBALS_H_INCLUDED

extern int debug_flags;

extern int Interrupted;

extern struct xyz Center;
extern struct xyz Bbox[2];

extern int Iteration;

extern char *CommandLine;

// definitions for command line args

extern int ToMinimize;
extern int IterPerFrame;
extern int NumFrames;
extern int DumpAsText;
extern int DumpIntermediateText;
extern int PrintFrameNums;
extern int OutputFormat;
extern int KeyRecordInterval;
extern int DirectEvaluate;
extern float ExcessiveEnergyLevel;
extern char *IDKey;
extern char *InputFileName;
extern char *OutputFileName;
extern char *TraceFileName;
extern char *BaseFileName;

extern FILE *OutputFile;
extern FILE *TraceFile;

extern int Count;

// have we warned the user about too much energy in a dynamics run?
extern int ExcessiveEnergyWarning;

// have we warned the user about using a generic/guessed force field parameter?
extern int ComputedParameterWarning;

extern int InterruptionWarning;

/** constants: timestep (.1 femtosecond), scale of distance (picometers) */
extern double Dt;
extern double Dx;
extern double Dmass;           // units of mass vs. kg
extern double Temperature;	/* Kelvins */
extern const double Boltz;	/* k, in J/K */
extern const double Pi;

extern double totClipped;  // internal thermostat for numerical stability

extern const double Gamma; // for Langevin thermostats

extern const double G1;

extern void reinit_globals(void);

#endif  /* GLOBALS_H_INCLUDED */
