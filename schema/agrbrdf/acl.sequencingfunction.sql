--
-- Name: sequencingfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE sequencingfunction FROM PUBLIC;
REVOKE ALL ON TABLE sequencingfunction FROM agrbrdf;
GRANT ALL ON TABLE sequencingfunction TO agrbrdf;
GRANT SELECT ON TABLE sequencingfunction TO gbs;


