Array::last = -> @[@length - 1]

graphs =
    minerals_income: {
        title: "Mineral income"
        allow_diff: true
    },
    minerals_gathered: {
        title: "Total minerals gathered"
        allow_diff: true
    },
    gas_income: {
        title: "Gas income"
        allow_diff: true
    },
    gas_gathered: {
        title: "Total gas gathered"
        allow_diff: true
    },
    supply_current: {
        title: "Current supply"
        allow_diff: false
    }
game_id = -1
update_timer = undefined;

zeroes = (val, n=2) ->
    s = "" + val
    while s.length < n
        s = "0" + s
    return s

format_game_time = (time) ->
    out = ""
    if time > 3600
        out += "#{ time // 3600  }:"
        time = time % 3600
    return out + "#{ zeroes(time // 60)}:#{ zeroes(time % 60) }"

load_live_content = ->
    game_id = $("#live_content").attr "data-game-id"

    $.getJSON "/live/get/livestats/?id=#{ game_id }", load_completed

load_completed = (data) ->
    $("#live_content").empty()
    load_header data
    setup_chart_menu()
    load_graphs data
    update_timer = setInterval refresh_data, 1000 

load_graphs = (data) ->

    stats = data.stats

    for graph_id of graphs
        graph = graphs[graph_id]
        $("#live_content").append(
            "<div id='live_#{ graph_id }' class='live-chart'></div>")

        player_1_data = ([x[0]["game_time"], x[0][graph_id]] for x in stats)
        player_2_data = ([x[0]["game_time"], x[1][graph_id]] for x in stats)


        series = [{
            id: "pla"
            name: data.pla.tag
            data: player_1_data
            linkedTo: "plb"
            showInLegend: true
        },
        {
            id: "plb"
            name: data.plb.tag
            data: player_2_data
            linkedTo: "pla"
            showInLegend: true
        }]

        if graph.allow_diff
            diff_data = ([
                x[0]["game_time"],
                x[1][graph_id]-x[0][graph_id]
                ] for x in stats)
            series.push {name: "Difference", data: diff_data}

        $("#live_#{ graph_id }").highcharts
            title: text: graph.title
            chart: animation: false
            exporting: enabled: false
            legend: enabled: false
            tooltip:
                crosshairs: true
                formatter: ->
                    ret = "<small>#{ format_game_time this.x }</small>
                        <table>"
                    for p in this.points
                        series = p.series
                        ret += "<tr><td>
                            <span style='color: #{ series.color }'>
                              #{ series.name }
                            </span></td><td><b>#{ p.y }</b></td></tr>"
                    ret + "</table>"
                shared: true
                useHTML: true
            xAxis: labels: formatter: ->
                format_game_time this.value
            plotOptions: series: marker: enabled: false
            series: series

load_header = (data) ->
    create_header()
    if data.stats[0]?
        update_header data

setup_chart_menu = ->

    get_linked_chart_div = (el) ->
        $("#live_#{ get_linked_chart_id el }")
    get_linked_chart_id = (el) ->
        $(el).attr("data-chart")
    
    $("#live_content").append("<div id='live_chart_menu'></div>")

    for graph_id of graphs
        $("#live_chart_menu").append "<div class='live-menu-item' data-chart='#{ graph_id }'></div>"

    $(".live-menu-item").each ->
        graph = get_linked_chart_id(this)
        $(this).append "<div class='live-menu-button-toggle'>#{ graphs[graph].title }</div>"

    $(".live-menu-button-toggle").click ->
        $("#live_#{ get_linked_chart_id(this.parentElement) }").toggle()

refresh_data = () ->
    $.getJSON "/live/get/livestats/?id=#{ game_id }&latest=1", (data) ->
        refresh_graphs data.stats
        refresh_header data

refresh_graphs = (stats) ->
    for graph_id in graphs
        series = $("#live_#{ graph_id }").highcharts().series

        if stats[0][0]?
            series[0].addPoint([stats[0][0]["game_time"], stats[0][0][graph_id]])
        if stats[0][1]?
            series[1].addPoint([stats[0][1]["game_time"], stats[0][1][graph_id]])

refresh_header = (data) ->
    if data.stats[0]?
        update_header data
    
create_header = ->
    $("#live_content").append("<div id='live_header'></div>")

format_supply = (current, cap) ->
    supply_string = "#{ current }/#{ cap }"
    if current > cap
        "<span class='supply-capped'>#{ supply_string }</span>"
    else
        supply_string

update_header = (data) ->
    last_stat = data.stats.last()
    pl1_supply = format_supply last_stat[0].supply_current, last_stat[0].supply_cap
    pl2_supply = format_supply last_stat[1].supply_current, last_stat[1].supply_cap
    timer = format_game_time last_stat[0].game_time
    
    $("#live_header").html "
        <div class='live-player'>
            <div class='live-player-top-row'>
                <a href='/players/#{ data.pla.id }'>
                    #{ data.pla.tag }
                </a>
                <div class='live-supply'>#{ pl1_supply }</div>
            </div>
            <div class='live-player-bottom-row'>
                <div class='live-minerals'>#{ last_stat[0].minerals_current }</div>
                <div class='live-gas'>#{ last_stat[0].gas_current }</div>
            </div>
        </div>
        <div class='live-timer'>#{ timer }</div>
        <div class='live-player'>
            <div class='live-player-top-row'>
                <div class='live-supply'>#{ pl2_supply }</div>
                <a href='/players/#{ data.plb.id }'>
                    #{ data.plb.tag }
                </a>
            </div>
            <div class='live-player-bottom-row'>
                <div class='live-gas'>#{ last_stat[1].gas_current }</div>
                <div class='live-minerals'>#{ last_stat[1].minerals_current }</div>
            </div>
        </div>"
