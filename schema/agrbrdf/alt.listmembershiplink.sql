--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY listmembershiplink
    ADD CONSTRAINT "$1" FOREIGN KEY (oblist) REFERENCES oblist(obid);


