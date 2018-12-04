var imagesBaseUrl = 'https://image.tmdb.org/t/p/w185';
var currentFilm;
var controlRelated = false;



function home(){
    var url_string = window.location.href;
    var url = new URL(url_string);
    var search = url.searchParams.get("search");
    if(search==null) {
        var element = document.getElementById('searchedFilm');
        element.innerHTML = '<div class="jumbotron jumbotron-fluid">' +
            '<div class="container">' +
            '<h2 class="display-4">Try to search a film.</h2>' +
            '<p class="lead"><small>The system will display possible search results and then try to compute similarity with other films by plot,actors,genders.</small></p>' +
            '</div>' +
            '</div>';
    }else{
        searchFilm();
    }

    meanPrecisions(true);


}




function searchFilm(){
    var url_string = window.location.href;
    var url = new URL(url_string);
    var id = url.searchParams.get("film");
    var search = url.searchParams.get("search");
    var filmToSearch = "";
    if(id!=null){
        filmToSearch = document.getElementById("filmSearch").value
        location.href='http://localhost:8000?search='+filmToSearch;
    }else{
        if(search==null)
            filmToSearch = document.getElementById("filmSearch").value;
        else
            filmToSearch = search;
    }

    if(filmToSearch!="") {
        var data = {film:filmToSearch};
        $.ajax({url:"/searchFilm",data:data,success: function(result){

            document.getElementById("filmSearch").value= "";
            var element = document.getElementById('searchedFilm');
            element.innerHTML = '<div class="ui styled accordion" id="accordion" style="width: 100%;height:45vh;overflow: scroll;">'+
                                +'</div';
            var accordion = document.getElementById("accordion");
            accordion.innerHTML="";

            for (i=0;i<result.results.length;i++){
                var attribute = "location.href='http://localhost:8000/film.html?film="+result.results[i].id+"'";
                if(result.results[i].overview!="") {
                    accordion.innerHTML += '<div class="title">' +
                        '<i class="dropdown icon"></i>' +
                        '<button name="filmButton" class="ui basic button" id="'+result.results[i].id+'" onclick="'+attribute+'">'+result.results[i].title+'</button>' +
                        '</div>' +
                        '<div class="content">' +
                        '<p class="transition hidden">' + result.results[i].overview + '</p>' +
                        '</div>';
                }
            }


            $('.ui.accordion')
               .accordion();



         }});


    }


}

function getFilmDetails(){
    var url_string = window.location.href;
    var url = new URL(url_string);
    var id = url.searchParams.get("film");
    var data = {id:id};
    $.ajax({url:"/getFilmDetails",data:data,success: function(result){
        document.getElementById("loading").innerHTML="";
        var genres ="";
        for(i=0;i<result.genres.length;i++){
            if(i!=(result.genres.length-1))
                genres+= result.genres[i].name+",";
            else
                genres+= result.genres[i].name;
        }
        var production = "";
        for(i=0;i<result.production_companies.length;i++){
            if(i!=(result.production_companies.length-1))
                production+= result.production_companies[i].name+",";
            else
                production+= result.production_companies[i].name;
        }
        var element = document.getElementById('searchedFilm');
        element.innerHTML='<div id="filmCardContainer" style="float:left;"></div>'+
                          '<div id="filmDetails" style="text-align: center;"></div>';
        var filmCardContainer = document.getElementById("filmCardContainer");
        var filmDetails = document.getElementById("filmDetails");
            filmCardContainer.innerHTML='<div class="ui card" style="width: 200px;height:480px">'+
                              '<div class="image" >'+
                              '<img src="'+imagesBaseUrl+result.poster_path+'">'+
                              '</div>'+
                              '<div class="content">'+
                              '<a class="header">'+result.title+'</a>'+
                              '<div class="meta">'+
                              '<span class="date">'+result.release_date+'<br>'+
                              '</div>'+
                              '<div class="description">'+
                              '</div>'+
                              '</div>'+
                              '<div class="extra content">'+
                              '<a>'+
                              '<i class="star outline icon"></i>'+
                              'IMDB Rating:'+result.vote_average+
                              '</a>'+
                              '</div>'+
                              '</div>';
         var actors="";
         for(i=0; i<10 && i<result.credits.cast.length;i++){
                actors+="<b>Actor: </b> "+result.credits.cast[i].name+"&nbsp&nbsp&nbsp&nbsp <b>Character: </b> "+result.credits.cast[i].character+"<br>";

         }
         filmDetails.innerHTML=result.overview+
                               '<br>'+
                                '<br>'+
                                '<br>'+
                               actors+
                              '<br>'+
                               '<br>'+
                               '<b>Production companies: </b> '+production+
                               '<br>'+
                                '<br>'+
                               '<b>Genres: </b>'+genres;

        relatedFilms(result.recommendations.results);
        currentFilm = id;
         $(window).scrollTop(0);

         if(controlRelated){

            var data = {currentFilm:currentFilm};
            $.ajax({url:"/relatedfilmsbyplot/",data:data,success: function(result) {


                displayRelatedBy(result.detailsPlot,result.precisionPlot,false,"byPlot","RELATED BY PLOT","postersPlot","evalPlot","listPlot","/static/images/plot.png");
                displayRelatedBy(result.detailsCompany,result.precisionCompany,true,"byCompany","RELATED BY PRODUCTION COMPANIES","postersCompany","evalCompany","listCompany","/static/images/production_companies.png");
                displayRelatedBy(result.detailsCast,result.precisionCast,true,"byCast","RELATED BY CAST MEMBERS","postersCast","evalCast","listCast","/static/images/cast.png");
                displayRelatedBy(result.detailsCrew,result.precisionCrew,true,"byCrew","RELATED BY CREW MEMBERS","postersCrew","evalCrew","listCrew","/static/images/crew.png");
                if(result.detailsGenres!=undefined && result.precisionGenres!=undefined)
                    displayRelatedBy(result.detailsGenres,result.precisionGenres,true,"byGenres","RELATED BY GENRES AND RANKED BY PLOT","postersGenres","evalGenres","listGenres","/static/images/genres.png");


                meanPrecisions(false)



            }});
      }

    }});





}

function relatedFilms(related){

    var relatedFilms = document.getElementById("relatedFilms");
    relatedFilms.innerHTML="";
    relatedFilms.innerHTML+="<br>";
    controlRelated = false;
    for(i=0;i<related.length;i++){
        controlRelated = true;
        var attribute = "location.href='http://localhost:8000/film.html?film="+related[i].id+"'";
        relatedFilms.innerHTML+='<div class="ui card" style="width: 200px;height:480px;float: left;">'+
                              '<div class="image" >'+
                              '<img src="'+imagesBaseUrl+related[i].poster_path+'">'+
                              '</div>'+
                              '<div class="content">'+
                              '<a class="header" id="'+related[i].id+'" onclick="'+attribute+'">'+related[i].title+'</a>'+
                              '<div class="meta">'+
                              '<span class="date">'+related[i].release_date+
                              '</div>'+
                              '<div class="description">'+
                               /*genres+*/
                              '</div>'+
                              '</div>'+
                              '<div class="extra content">'+
                              '<a>'+
                              '<i class="star outline icon"></i>'+
                              'IMDB Rating:'+related[i].vote_average+
                              '</a>'+
                              '</div>'+
                              '</div>';






    }
    var analyzedFilms = document.getElementById("analyzedFilms");
    if(controlRelated) {

        analyzedFilms.innerHTML = '<div class="ui segment">' +
            '<div class="ui active inverted dimmer">' +
            '<div class="ui text loader">Loading</div>' +
            '</div>' +
            '<p></p>' +
            '</div>';





    }else{
        analyzedFilms.innerHTML = '<div class="alert alert-danger" role="alert">'+
                                  'No related films to analyze!'
                                  '</div>';
    }






}



 function displayRelatedBy(related,precision,appending,divBy,text,divPoster,divEval,divList,imageSrc){
     console.log("relatedBy");
     var analyzed = document.getElementById("analyzedFilms");
     if(appending)
        analyzed.innerHTML+='<br><br><br>'+
                            '<div id="'+divBy+'"></div>';
     else
          analyzed.innerHTML='<div id="'+divBy+'"></div>';
     var by = document.getElementById(divBy);
     var eval = "'eval'";
     var posters = "'posters'";
     var postersDiv = "'"+divPoster+"'";
     var evalDiv = "'"+divEval+"'";
     by.innerHTML='<h4><small><b>'+text+'</b></small></h4>'+
                      '<div class="ui large buttons">'+
                      '<button class="ui button" onclick="swapTab('+posters+','+postersDiv+','+evalDiv+')">Posters</button>'+
                      '<div class="or"></div>'+
                      '<button class="ui button" onclick="swapTab('+eval+','+postersDiv+','+evalDiv+')">List and Evaluation</button>'+
                      '</div>'+
                      '<br><br>'+
                      '<div id="'+divPoster+'" style="display: none;"></div>'+
                      '<br><br>'+
                      '<div id="'+divEval+'"></div>';

     var postersDiv = document.getElementById(divPoster);
     postersDiv.innerHTML+="<br>";
     var evalDiv = document.getElementById(divEval);
     var date = new Date();
     var time = date.getTime();
     evalDiv.innerHTML='<div class="ui link list" id="'+divList+'" style="float: left;"></div>';
     evalDiv.innerHTML+='<div class="ui big images">'+
                        '<img class="ui image" src="'+imageSrc+'?'+time+'">'+
                        '</div>'+
                        '<br>'+
                        '<div class="ui label">'+
                        'Precision'+
                        '<div class="detail">'+precision+'</div>'+
                        '</div>';

     var List = document.getElementById(divList);
     for(i=0;i<related.length;i++){
         var attribute = "location.href='http://localhost:8000/film.html?film="+related[i].id+"'";
         postersDiv.innerHTML+='<div class="ui card" style="width: 200px;height:480px;float: left;">'+
                              '<div class="image" >'+
                              '<img src="'+imagesBaseUrl+related[i].poster_path+'">'+
                              '</div>'+
                              '<div class="content">'+
                              '<a class="header" id="'+related[i].id+'" onclick="'+attribute+'">'+related[i].title+'</a>'+
                              '<div class="meta">'+
                              '<span class="date">'+related[i].release_date+
                              '</div>'+
                              '<div class="description">'+
                               /*genres+*/
                              '</div>'+
                              '</div>'+
                              '<div class="extra content">'+
                              '<a>'+
                              '<i class="star outline icon"></i>'+
                              'IMDB Rating:'+related[i].vote_average+
                              '</a>'+
                              '</div>'+
                              '</div>';

         List.innerHTML+='<a class="item" onclick="'+attribute+'" id="'+related[i].id+'">'+related[i].title+'</a>';









    }
    postersDiv.innerHTML+='<br><br>';
 }

 function swapTab(tab,postersDiv,evalDiv){
     var posters = document.getElementById(postersDiv);
     var eval = document.getElementById(evalDiv);
     if(tab=="posters"){
         posters.style="display:inline-block;";
         eval.style="display:none";

     }else if(tab=="eval"){
         posters.style="display:none;";
         eval.style="display:inline;";
     }

 }



 function meanPrecisions(homepage){
     var element = document.getElementById("meanPrecisions");


    $.ajax({url:"/filmsaverageprecisions",success:function (result) {
         if(homepage) {

             element.innerHTML = '<div><b>Mean Precisions on ' + result[0].count + ' tests:</b></div><br>' +
                 '<div class="ui middle aligned divided list">' +
                 '<div class="item">' +
                 '<div class="right floated content">' +
                 '<div class="ui circular basic label">' + (result[0].avg_plot).toFixed(2) + '</div>' +
                 '</div>' +
                 '<div class="content">' +
                 '<b>By Plot:</b>' +
                 '</div>' +
                 '</div>' +
                 '<div class="item">' +
                 '<div class="right floated content">' +
                 '<div class="ui circular basic label">' + (result[0].avg_cast).toFixed(2) + '</div>' +
                 '</div>' +
                 '<div class="content">' +
                 '<b>By Cast:</b>' +
                 '</div>' +
                 '</div>' +
                 '<div class="item">' +
                 '<div class="right floated content">' +
                 '<div class="ui circular basic label">' + (result[0].avg_crew).toFixed(2) + '</div>' +
                 '</div>' +
                 '<div class="content">' +
                 '<b>By Crew:</b>' +
                 '</div>' +
                 '</div>' +
                 '<div class="item">' +
                 '<div class="right floated content">' +
                 '<div class="ui circular basic label">' + (result[0].avg_company).toFixed(2) + '</div>' +
                 '</div>' +
                 '<div class="content">' +
                 '<b>By Company:</b>' +
                 '</div>' +
                 '</div>' +
                 '<div class="item">' +
                 '<div class="right floated content">' +
                 '<div class="ui circular basic label">' + (result[0].avg_genres).toFixed(2) + '</div>' +
                 '</div>' +
                 '<div class="content">' +
                 '<b>By genres:<b/>' +
                 '</div>' +
                 '</div>' +
                 '</div>';

         }else{

             element.innerHTML = '<div><b>Mean Precisions on ' + result[0].count + ' tests:</b></div><br>' +
                                 '<div class="ui middle aligned divided list">' +
                                 '<div class="item">' +
                                 '<div class="right floated content">' +
                                 '<div class="ui circular basic label">' + (result[0].avg_plot).toFixed(2) + '</div>' +
                                 '</div>' +
                                 '<div class="content">' +
                                 '<a href="#byPlot"><b>By Plot:</b></a>' +
                                 '</div>' +
                                 '</div>' +
                                 '<div class="item">' +
                                 '<div class="right floated content">' +
                                 '<div class="ui circular basic label">' + (result[0].avg_cast).toFixed(2) + '</div>' +
                                 '</div>' +
                                 '<div class="content">' +
                                 '<a href="#byCast"><b>By Cast:</b></a>' +
                                 '</div>' +
                                 '</div>' +
                                 '<div class="item">' +
                                 '<div class="right floated content">' +
                                 '<div class="ui circular basic label">' + (result[0].avg_crew).toFixed(2) + '</div>' +
                                 '</div>' +
                                 '<div class="content">' +
                                 '<a href="#byCrew"><b>By Crew:</b></a>' +
                                 '</div>' +
                                 '</div>' +
                                 '<div class="item">' +
                                 '<div class="right floated content">' +
                                 '<div class="ui circular basic label">' + (result[0].avg_company).toFixed(2) + '</div>' +
                                 '</div>' +
                                 '<div class="content">' +
                                 '<a href="#byCompany"><b>By Company:</b></a>' +
                                 '</div>' +
                                 '</div>' +
                                 '<div class="item">' +
                                 '<div class="right floated content">' +
                                 '<div class="ui circular basic label">' + (result[0].avg_genres).toFixed(2) + '</div>' +
                                 '</div>' +
                                 '<div class="content">' +
                                 '<a href="#byGenres"><b>By genres:<b/></a>' +
                                 '</div>' +
                                 '</div>' +
                                 '</div>'+
                                 '<a href="#labelSearchedFilm">Searched Film</a><br><br>'+
                                 '<a href="#labelRelatedFilms">Related Films</a>';

         }
    }});

 }
























