--
-- Name: microarrayobservation; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE microarrayobservation FROM PUBLIC;
REVOKE ALL ON TABLE microarrayobservation FROM agrbrdf;
GRANT ALL ON TABLE microarrayobservation TO agrbrdf;
GRANT SELECT ON TABLE microarrayobservation TO gbs;


