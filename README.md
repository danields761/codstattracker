# COD Stat Tracker

The simple app aimed to collect your matches history on daily basis and provide historical info about performance.

Uses semi-official API as my.activision.com does.

## Structure

* codstattracker.poller - entrypoint which should be executed in order to obtain and persist stats, there is also Python API for this
* codstattracer.views - WEB-handlers which provides collected stats in various ways (there is also Python API located at `codstattracker.storage`)
