import React, { Component } from 'react'
import axios from 'axios'
import { Badge, Button, Card, CardDeck, CardTitle, CardBody, CardHeader, CardText, Col, Form, FormGroup, Input, Label} from 'reactstrap'
import update from 'react-addons-update'
import { withRouter } from "react-router-dom";
import PropTypes from 'prop-types'
import Utils from '../classes/utils'
import { Link, Redirect } from 'react-router-dom'

export default class FilesTable extends Component {
  constructor (props) {
    super(props)
    this.utils = new Utils()
  }

  render () {

    if (this.props.files.length == 0) {
        return (
            <div className="container">
            <h2>No files available</h2>
            </div>
        )
    }

    const setStatus = (file_status) => {
        let status = <div></div>
        if (file_status == "available"){
            status = <Badge color="success">Available</Badge>
        }
        if (file_status == "unavailable" || file_status == "failed"){
            status = <Badge color="danger">Unavailable</Badge>
        }
        if (file_status == "pulling"){
            status = <Badge color="secondary">Pulling</Badge>
        }
        if (file_status == "pullable"){
            status = <Badge color="started">Pullable</Badge>
        }
        if (file_status == "starting" || file_status == "hashing"){
            status = <Badge color="warning">Publishing</Badge>
        }
        return status
    }

    let content = this.props.files.map((item, i) => (
        <div key={i}>
        <Card>
          <CardHeader tag="h4">{setStatus(item.status)} <Badge pill color="primary" className="float-right">v{item.version}</Badge></CardHeader>
          <CardBody>
            <CardTitle tag="h3"><i className="fas fa-file"></i> File : <Link to={"/files/" + item.uri}>{item.file_name}</Link></CardTitle>
            <CardText>
            Size : {this.utils.humanFileSize(item.size, true)}
            <br/>
            Published : {item.publishing_date}
            <br/>
            Downloads : {item.downloads}
            </CardText>
          </CardBody>
        </Card>
        </div>
      ))

    return (
      <div className="container">
        <h2 className="text-center">{this.props.files.length} {this.props.files.length == 1 ? "file" : "files"} found</h2>
        <br/>
        {content}
      </div>
    )
  }
}

FilesTable.propTypes = {
  config: PropTypes.object,
  files: PropTypes.array
}

