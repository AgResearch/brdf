--
-- Name: datasourcelistmembershiplink_datasourcelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcelistmembershiplink
    ADD CONSTRAINT datasourcelistmembershiplink_datasourcelist_fkey FOREIGN KEY (datasourcelist) REFERENCES datasourcelist(obid);


--
-- Name: datasourcelistmembershiplink_datasourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY datasourcelistmembershiplink
    ADD CONSTRAINT datasourcelistmembershiplink_datasourceob_fkey FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


