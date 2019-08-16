--
-- Name: ob_pkey; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY ob
    ADD CONSTRAINT ob_pkey PRIMARY KEY (obid);


--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ob
    ADD CONSTRAINT "$1" FOREIGN KEY (obtypeid) REFERENCES obtype(obtypeid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ob
    ADD CONSTRAINT "$2" FOREIGN KEY (statuscode) REFERENCES obstatus(statuscode);


