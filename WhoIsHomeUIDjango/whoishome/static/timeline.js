(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(require('chart.js'), require('moment')) :
    typeof define === 'function' && define.amd ? define(['chart.js', 'moment'], factory) :
    (factory(global.Chart,global.moment));
}(this, (function (Chart,moment) { 'use strict';

    Chart = Chart && Chart.hasOwnProperty('default') ? Chart['default'] : Chart;
    moment = moment && moment.hasOwnProperty('default') ? moment['default'] : moment;

    const helpers = Chart.helpers;
    const isArray = helpers.isArray;

    var _color = Chart.helpers.color;

    var TimelineConfig = {
        position: 'bottom',

        tooltips: {
            mode: 'nearest',
        },
        adapters: {},
        time: {
            parser: false, // false == a pattern string from http://momentjs.com/docs/#/parsing/string-format/ or a custom callback that converts its argument to a moment
            format: false, // DEPRECATED false == date objects, moment object, callback or a pattern string from http://momentjs.com/docs/#/parsing/string-format/
            unit: false, // false == automatic or override with week, month, year, etc.
            round: false, // none, or override with week, month, year, etc.
            displayFormat: false, // DEPRECATED
            isoWeekday: false, // override week start day - see http://momentjs.com/docs/#/get-set/iso-weekday/
            minUnit: 'millisecond',
            distribution: 'linear',
            bounds: 'data',

            // defaults to unit's corresponding unitFormat below or override using pattern string from http://momentjs.com/docs/#/displaying/format/
            displayFormats: {
                millisecond: 'h:mm:ss.SSS a', // 11:20:01.123 AM,
                second: 'h:mm:ss a', // 11:20:01 AM
                minute: 'h:mm a', // 11:20 AM
                hour: 'DD-MMM HH:00', // 5PM
                day: 'DD-M HH:00', // Sep 4
                week: 'll', // Week 46, or maybe "[W]WW - YYYY" ?
                month: 'MMM YYYY', // Sept 2015
                quarter: '[Q]Q - YYYY', // Q3
                year: 'YYYY' // 2015
            },
        },
        ticks: {
            autoSkip: true,
            maxTicksLimit: 5,
        }
    };


    /**
     * Convert the given value to a moment object using the given time options.
     * @see http://momentjs.com/docs/#/parsing/
     */
    function momentify(value, options) {
        var parser = options.parser;
        var format = options.parser || options.format;

        if (typeof parser === 'function') {
            return parser(value);
        }

        if (typeof value === 'string' && typeof format === 'string') {
            return moment(value, format);
        }

        if (!(value instanceof moment)) {
            value = moment(value);
        }

        if (value.isValid()) {
            return value;
        }

        // Labels are in an incompatible moment format and no `parser` has been provided.
        // The user might still use the deprecated `format` option to convert his inputs.
        if (typeof format === 'function') {
            return format(value);
        }

        return value;
    }

    function parse(input, scale) {
        if (helpers.isNullOrUndef(input)) {
            return null;
        }

        var options = scale.options.time;
        var value = momentify(scale.getRightValue(input), options);
        if (!value.isValid()) {
            return null;
        }

        if (options.round) {
            value.startOf(options.round);
        }

        return value.valueOf();
    }

    var MIN_INTEGER = Number.MIN_SAFE_INTEGER || -9007199254740991;
    var MAX_INTEGER = Number.MAX_SAFE_INTEGER || 9007199254740991;

    var TimelineScale = Chart.scaleService.getScaleConstructor('time').extend({

        determineDataLimits: function() {
            var me = this;
            var chart = me.chart;
            var timeOpts = me.options.time;
            var elemOpts = me.chart.options.elements;
            var min = MAX_INTEGER;
            var max = MIN_INTEGER;
            var timestamps = [];
            var timestampobj = {};
            var datasets = [];
            var i, j, ilen, jlen, data, timestamp0, timestamp1;


            // Convert data to timestamps
            for (i = 0, ilen = (chart.data.datasets || []).length; i < ilen; ++i) {
                if (chart.isDatasetVisible(i)) {
                    data = chart.data.datasets[i].data;
                    datasets[i] = [];

                    for (j = 0, jlen = data.length; j < jlen; ++j) {
                        timestamp0 = parse(data[j][elemOpts.keyStart], me);
                        timestamp1 = parse(data[j][elemOpts.keyEnd], me);
                        if (timestamp0 > timestamp1) {
                            [timestamp0, timestamp1] = [timestamp1, timestamp0];
                        }
                        if (min > timestamp0 && timestamp0) {
                            min = timestamp0;
                        }
                        if (max < timestamp1 && timestamp1) {
                            max = timestamp1;
                        }
                        datasets[i][j] = [timestamp0, timestamp1, data[j][elemOpts.keyValue]];
                        if (!timestampobj.hasOwnProperty(timestamp0)) {
                            timestampobj[timestamp0] = true;
                            timestamps.push(timestamp0);
                        }
                        if (!timestampobj.hasOwnProperty(timestamp1)) {
                            timestampobj[timestamp1] = true;
                            timestamps.push(timestamp1);
                        }
                    }
                } else {
                    datasets[i] = [];
                }
            }

            if (timestamps.size) {
                timestamps.sort(function (a, b){
                    return a - b;
                });
            }

            min = parse(timeOpts.min, me) || min;
            max = parse(timeOpts.max, me) || max;

            // In case there is no valid min/max, var's use today limits
            min = min === MAX_INTEGER ? +moment().startOf('day') : min;
            max = max === MIN_INTEGER ? +moment().endOf('day') + 1 : max;

            // Make sure that max is strictly higher than min (required by the lookup table)
            me.min = Math.min(min, max);
            me.max = Math.max(min + 1, max);

            // PRIVATE
            me._horizontal = me.isHorizontal();
            me._table = [];
            me._timestamps = {
                data: timestamps,
                datasets: datasets,
                labels: []
            };
        },
    });

    Chart.scaleService.registerScaleType('timeline', TimelineScale, TimelineConfig);

    Chart.controllers.timeline = Chart.controllers.bar.extend({

        getBarBounds : function (bar) {
            var vm =   bar._view;
            var x1, x2, y1, y2;

            x1 = vm.x;
            x2 = vm.x + vm.width;
            y1 = vm.y;
            y2 = vm.y + vm.height;

            return {
                left : x1,
                top: y1,
                right: x2,
                bottom: y2
            };

        },

        update: function(reset) {
            var me = this;
            var meta = me.getMeta();
            var chartOpts = me.chart.options;
            if (chartOpts.textPadding || chartOpts.minBarWidth ||
                    chartOpts.showText || chartOpts.colorFunction) {
                var elemOpts = me.chart.options.elements;
                elemOpts.textPadding = chartOpts.textPadding || elemOpts.textPadding;
                elemOpts.minBarWidth = chartOpts.minBarWidth || elemOpts.minBarWidth;
                elemOpts.colorFunction = chartOpts.colorFunction || elemOpts.colorFunction;
                elemOpts.minBarWidth = chartOpts.minBarWidth || elemOpts.minBarWidth;
                if (Chart._tl_depwarn !== true) {
                    console.log('Timeline Chart: Configuration deprecated. Please check document on Github.');
                    Chart._tl_depwarn = true;
                }
            }

            helpers.each(meta.data, function(rectangle, index) {
                me.updateElement(rectangle, index, reset);
            }, me);
        },

        updateElement: function(rectangle, index, reset) {
            var me = this;
            var meta = me.getMeta();
            var xScale = me.getScaleForId(meta.xAxisID);
            var yScale = me.getScaleForId(meta.yAxisID);
            var dataset = me.getDataset();
            var data = dataset.data[index];
            var custom = rectangle.custom || {};
            var datasetIndex = me.index;
            var opts = me.chart.options;
            var elemOpts = opts.elements || Chart.defaults.timeline.elements;
            var rectangleElementOptions = elemOpts.rectangle;
            var textPad = elemOpts.textPadding;
            var minBarWidth = elemOpts.minBarWidth;

            rectangle._xScale = xScale;
            rectangle._yScale = yScale;
            rectangle._datasetIndex = me.index;
            rectangle._index = index;

            var text = data[elemOpts.keyValue];

            var ruler = me.getRuler(index);

            var x = xScale.getPixelForValue(data[elemOpts.keyStart]);
            var end = xScale.getPixelForValue(data[elemOpts.keyEnd]);

            var y = yScale.getPixelForValue(data, datasetIndex, datasetIndex);
            var width = end - x;
            var height = me.calculateBarHeight(ruler);
            var color = _color(elemOpts.colorFunction(text, data, dataset, index));
            var showText = elemOpts.showText;

            var font = elemOpts.font;

            if (!font) {
                font = '12px bold Arial';
            }

            // This one has in account the size of the tick and the height of the bar, so we just
            // divide both of them by two and subtract the height part and add the tick part
            // to the real position of the element y. The purpose here is to place the bar
            // in the middle of the tick.
            var boxY = y - (height / 2);

            rectangle._model = {
                x: reset ?  x - width : x,   // Top left of rectangle
                y: boxY , // Top left of rectangle
                width: Math.max(width, minBarWidth),
                height: height,
                base: x + width,
                backgroundColor: color.rgbaString(),
                borderSkipped: custom.borderSkipped ? custom.borderSkipped : rectangleElementOptions.borderSkipped,
                borderColor: custom.borderColor ? custom.borderColor : helpers.getValueAtIndexOrDefault(dataset.borderColor, index, rectangleElementOptions.borderColor),
                borderWidth: custom.borderWidth ? custom.borderWidth : helpers.getValueAtIndexOrDefault(dataset.borderWidth, index, rectangleElementOptions.borderWidth),
                // Tooltip
                label: me.chart.data.labels[index],
                datasetLabel: dataset.label,
                text: text,
                textColor: color.luminosity() > 0.5 ? '#000000' : '#ffffff',
            };

            rectangle.draw = function() {
                var ctx = this._chart.ctx;
                var vm = this._view;
                var oldAlpha = ctx.globalAlpha;
                var oldOperation = ctx.globalCompositeOperation;

                // Draw new rectangle with Alpha-Mix.
                ctx.fillStyle = vm.backgroundColor;
                ctx.lineWidth = vm.borderWidth;
                ctx.globalCompositeOperation = 'destination-over';
                ctx.fillRect(vm.x, vm.y, vm.width, vm.height);

                ctx.globalAlpha = 0.5;
                ctx.globalCompositeOperation = 'source-over';
                ctx.fillRect(vm.x, vm.y, vm.width, vm.height);

                ctx.globalAlpha = oldAlpha;
                ctx.globalCompositeOperation = oldOperation;
                if (showText) {
                    ctx.beginPath();
                    var textRect = ctx.measureText(vm.text);
                    if (textRect.width > 0 && textRect.width + textPad + 2 < vm.width) {
                        ctx.font = font;
                        ctx.fillStyle = vm.textColor;
                        ctx.lineWidth = 0;
                        ctx.strokeStyle = vm.textColor;
                        ctx.textBaseline = 'middle';
                        ctx.fillText(vm.text, vm.x + textPad, vm.y + (vm.height) / 2);
                    }
                    ctx.fill();
                }
            };

            rectangle.inXRange = function (mouseX) {
                var bounds = me.getBarBounds(this);
                return mouseX >= bounds.left && mouseX <= bounds.right;
            };
            rectangle.tooltipPosition = function () {
                var vm = this.getCenterPoint();
                return {
                    x: vm.x ,
                    y: vm.y
                };
            };

            rectangle.getCenterPoint = function () {
                var vm = this._view;
                var x, y;
                x = vm.x + (vm.width / 2);
                y = vm.y + (vm.height / 2);

                return {
                    x : x,
                    y : y
                };
            };

            rectangle.inRange = function (mouseX, mouseY) {
                var inRange = false;

                if(this._view)
                {
                    var bounds = me.getBarBounds(this);
                    inRange = mouseX >= bounds.left && mouseX <= bounds.right &&
                        mouseY >= bounds.top && mouseY <= bounds.bottom;
                }
                return inRange;
            };

            rectangle.pivot();
        },

        getBarCount: function() {
            var me = this;
            var barCount = 0;
            helpers.each(me.chart.data.datasets, function(dataset, datasetIndex) {
                var meta = me.chart.getDatasetMeta(datasetIndex);
                if (meta.bar && me.chart.isDatasetVisible(datasetIndex)) {
                    ++barCount;
                }
            }, me);
            return barCount;
        },


        // draw
        draw: function (ease) {
            var easingDecimal = ease || 1;
            var i, len;
            var metaData = this.getMeta().data;
            for (i = 0, len = metaData.length; i < len; i++)
            {
                metaData[i].transition(easingDecimal).draw();
            }
        },

        // From controller.bar
        calculateBarHeight: function(ruler) {
            var me = this;
            var yScale = me.getScaleForId(me.getMeta().yAxisID);
            if (yScale.options.barThickness) {
                return yScale.options.barThickness;
            }
            return yScale.options.stacked ? ruler.categoryHeight : ruler.barHeight;
        },

        removeHoverStyle: function(e) {
            //
        },

        setHoverStyle: function(e) {
        //
        }

    });


    Chart.defaults.timeline = {
        elements: {
            colorFunction: function() {
                return '#404060';
            },
            showText: true,
            textPadding: 4,
            minBarWidth: 1,
            keyStart: 0,
            keyEnd: 1,
            keyValue: 2
        },

        layout: {
            padding: {
                left: 0,
                right: 0,
                top: 0,
                bottom: 0
            }
        },

        legend: {
            display: false
        },

        scales: {
            xAxes: [{
                type: 'timeline',
                position: 'bottom',
                distribution: 'linear',
                categoryPercentage: 0.8,
                barPercentage: 0.9,

                gridLines: {
                    display: true,
                    // offsetGridLines: true,
                    drawBorder: true,
                    drawTicks: true
                },
                ticks: {
                    maxRotation: 0
                },
                unit: 'day'
            }],
            yAxes: [{
                type: 'category',
                position: 'left',
                barThickness : 20,
                categoryPercentage: 0.8,
                barPercentage: 0.9,
                offset: true,
                gridLines: {
                    display: true,
                    offsetGridLines: true,
                    drawBorder: true,
                    drawTicks: true
                }
            }]
        },
        tooltips: {
            callbacks: {
                title: function(tooltipItems, data) {
                    var elemOpts = this._chart.options.elements;
                    var d = data.labels[tooltipItems[0].datasetIndex];
                    return d;
                },
                label: function(tooltipItem, data) {
                    var elemOpts = this._chart.options.elements;
                    var d = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index];
                    return [d[elemOpts.keyValue], moment(d[elemOpts.keyStart]).format('L LTS'), moment(d[elemOpts.keyEnd]).format('L LTS')];
                }
            }
        }
    };

})));
