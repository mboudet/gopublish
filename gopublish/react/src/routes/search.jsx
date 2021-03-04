import React, { Component } from 'react'
import axios from 'axios'
import { Badge, Button, Card, CardTitle, CardBody, CardText, Form, FormGroup, Input, Label} from 'reactstrap'
import update from 'react-addons-update'
import { withRouter } from "react-router-dom";
import PropTypes from 'prop-types'
import Utils from '../classes/utils'
import { Link, Redirect } from 'react-router-dom'

class Search extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
  }

  render () {
    if (this.props.location.state.results.length == 0) {
        return (
            <div className="container">
            <h2>No files found</h2>
            </div>
        )
    };

    const setStatus = (file_status) => {
        let status = <div></div>
        if (file_status == "available"){
            status = <Badge className="float-right" color="success">Available</Badge>
        }
        if (file_status == "unavailable" || file_status == "failed"){
            status = <Badge className="float-right" color="danger">Unavailable</Badge>
        }
        if (file_status == "pulling"){
            status = <Badge className="float-right" color="secondary">Pulling</Badge>
        }
        if (file_status == "pullable"){
            status = <Badge className="float-right" color="started">Pullable</Badge>
        }
        if (file_status == "starting" || file_status == "hashing"){
            status = <Badge className="float-right" color="warning">Publishing</Badge>
        }
        return status
    }

    let content = this.props.location.state.results.map((item, i) => (
        <div key={i}>
        <Card>
          <CardBody>
            <CardTitle tag="h3"><i className="fas fa-file"></i> File : <Link to={"/files/" + item.uri}>{item.file_name}</Link>{setStatus(item.status)}</CardTitle>
            <CardText>
            File version : {item.version}
            <br/>
            Size : {this.utils.humanFileSize(item.size, true)}
            <br/>
            Downloads : {item.downloads}
            </CardText>
          </CardBody>
        </Card>
        <br/>
        </div>
      ))

    return (
      <div className="container">
        <h2 className="text-center">{this.props.location.state.results.length} {this.props.location.state.results.length == 1 ? "file" : "files"} found</h2>
        <br/>
        {content}
      </div>
    )
  }
}

Search.propTypes = {
  config: PropTypes.object,
  location: PropTypes.object
}

export default withRouter(Search)
