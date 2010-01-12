

function plot_hdd(dev, data) {

    var labels = [];
    var values = [];
    for (i in data.items) {
        var item = data.items[i];
        labels.push(item.label);
        values.push(item.data);
    }

    var r = Raphael(dev);
    r.g.txtattr.font = "12px 'Fontin Sans', Fontin-Sans, sans-serif";

    r.g.text(120, 100, "Disco hda").attr({"font-size": 20});

    var pie = r.g.piechart(320, 240, 100, values, {legend: labels, legendpos: "west"});
    pie.hover(function () {
        this.sector.stop();
        this.sector.scale(1.1, 1.1, this.cx, this.cy);
        if (this.label) {
            this.label[0].stop();
            this.label[0].scale(1.5);
            this.label[1].attr({"font-weight": 800});
        }
        }, function () {
            this.sector.animate({scale: [1, 1, this.cx, this.cy]}, 500, "bounce");
            if (this.label) {
                this.label[0].animate({scale: 1}, 500, "bounce");
                this.label[1].attr({"font-weight": 400});
        }
    });
}
