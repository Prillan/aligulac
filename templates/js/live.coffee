Array::last = -> @[@length - 1]

graphs = ["supply_current", "minerals_income", "minerals_gathered"]
game_id = -1

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
    load_graphs data
    setInterval refresh_data, 1000 

load_graphs = (data) ->

    for graph_id in graphs
        $("#live_content").append(
            "<div id='live_#{ graph_id }' class='live-chart'></div>")

        player_1_data = ([x[0]["game_time"], x[0][graph_id]] for x in data)
        player_2_data = ([x[0]["game_time"], x[1][graph_id]] for x in data)

        $("#live_#{ graph_id }").highcharts
            title: {text: graph_id, x: -20}
            chart: {animation: false}
            tooltip: {enabled: false}
            plotOptions: {series: marker: enabled: false }
            series: [
                {
                    name: "Player 1",
                    data: player_1_data},
                {
                    name: "Player 2",
                    data: player_2_data},
            ]
load_header = (data) ->
    create_header()
    if data[0]?
        update_header data.last()

refresh_data = () ->
    $.getJSON "/live/get/livestats/?id=#{ game_id }&latest=1", (data) ->
        refresh_graphs data
        refresh_header data

refresh_graphs = (data) ->
    for graph_id in graphs
        series = $("#live_#{ graph_id }").highcharts().series

        if data[0][0]?
            series[0].addPoint([data[0][0]["game_time"], data[0][0][graph_id]])
        if data[0][1]?
            series[1].addPoint([data[0][1]["game_time"], data[0][1][graph_id]])

refresh_header = (data) ->
    if data[0]?
        update_header data[0]
    
create_header = ->
    $("#live_content").append("<div id='live_header'></div>")

update_header = (data) ->
    pl1_supply = "#{ data[0].supply_current }/#{ data[0].supply_cap }"
    pl2_supply = "#{ data[1].supply_current }/#{ data[1].supply_cap }"
    timer = format_game_time data[0].game_time
    
    $("#live_header").html "<h2>#{ pl1_supply } -- #{ timer } -- #{ pl2_supply }</h2>"
$(document).ready(load_live_content)
