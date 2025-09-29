import React from 'react';
import ReactDOM from 'react-dom/client';
import activities from './data.json';
import './index.css';
import reportWebVitals from './reportWebVitals';

function getDailyTime(timestamp){
  var newTimestamp = parseInt(timestamp);
  const time = new Date(newTimestamp).toLocaleTimeString();
  return time
}

class CardList extends React.Component {
  state = {
    listitems: [{"List Item 1": 1}, {"List Item 2": 2}, {"List Item 3": 3}]
  };

  render(){
    return(
      <div>
          <ul className='list'>
            {activities.map((activity, i, array) => 
              (
              <Card activity={activity} prev={array[i - 1]} key={i}/>
            )
            )}
          </ul>       
      </div>
    );
  }
}

class Card extends React.Component{
  placeCard(){
    return(<p>{this.props.activity.placeName + ' ' + new Date(parseInt(this.props.activity.startTime)).toLocaleTimeString()}</p>)
  }

  textCard(){
    return(
      
      <div>
        <div class='new-day'>{this.newDay()}</div>
        <div class='text-card'>
        <p>{this.props.activity.contactName === this.props.prev.contactName ? null : this.props.activity.contactName}</p>
        <p>{this.props.activity.body}</p>
        <p>{getDailyTime(this.props.activity.startTime)}</p>
        <p>From {this.props.activity.type === '2' ? 'Me' : this.props.activity.contactName}</p>
        </div>
      </div>
    
    )
  }

  activityCard(){
    return(
      <p>{this.props.activity.activityType}</p>
    )
  }

  // Inserts date if the day changes between the last and current card
  newDay(){
    var currDay = new Date(parseInt(this.props.activity.startTime));
    var prevDay = new Date(parseInt(this.props.prev.startTime));

    if (currDay.getDate() !== prevDay.getDate()){
      return(
        <p>{currDay.toLocaleDateString('en-US', {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'})}</p>
      )
    }
  }

  render(){
    switch(this.props.activity.name){
      case 'placeVisit':
        return(<div>{this.placeCard()}</div>)
      case 'text':
        return(<div>{this.textCard()}</div>)
      case 'activitySegment':
        return(<div>{this.activityCard()}</div>)
      default:
        return(<p>Can't find activity type</p>)

    }
  }
}
  // ========================================
  
  const root = ReactDOM.createRoot(document.getElementById("root"));
  root.render(<CardList />);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
